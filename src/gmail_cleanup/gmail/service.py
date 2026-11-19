"""Gmail authentication, account selection and safe cleanup operations."""

from __future__ import annotations

import json
import logging
import os
import re
import stat
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from dotenv import dotenv_values, set_key
from google.auth.credentials import Credentials as BaseCredentials
from google.auth.exceptions import GoogleAuthError
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from httplib2 import HttpLib2Error
from keyring.backends.macOS import Keyring

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]
KEYRING_SERVICE = "gmail-cleanup"
ACCOUNT_INDEX = "__accounts__"

# OAuth callback URLs can contain authorization codes.
logging.getLogger("google_auth_oauthlib.flow").setLevel(logging.WARNING)


class ConfigurationError(Exception):
    """The application cannot use its configured credentials."""


def setting(name: str) -> str | None:
    """Read an environment value, falling back to .env in the current directory."""
    value = os.environ.get(name)
    if value is not None:
        return value
    return dotenv_values(Path.cwd() / ".env").get(name)


def _keyring() -> Keyring:
    if sys.platform != "darwin":
        raise ConfigurationError("Account storage requires macOS Keychain.")
    return Keyring()


def accounts() -> list[str]:
    raw = _keyring().get_password(KEYRING_SERVICE, ACCOUNT_INDEX)
    if raw is None:
        return []
    try:
        result = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ConfigurationError("The Keychain account index is invalid.") from exc
    if not isinstance(result, list) or not all(isinstance(item, str) for item in result):
        raise ConfigurationError("The Keychain account index is invalid.")
    return result


def client_config(path: str | None = None, value: str | None = None) -> dict[str, Any]:
    """Load an OAuth desktop-client configuration without exposing its contents."""
    if value is not None or path is not None:
        config_value, config_path = value, path
    else:
        config_value = setting("GMAIL_CLIENT_CONFIG_JSON")
        config_path = setting("GMAIL_CREDENTIALS_PATH")
    if config_value:
        raw = config_value
    elif config_path:
        try:
            raw = Path(config_path).expanduser().read_text(encoding="utf-8")
        except OSError as exc:
            raise ConfigurationError("Cannot read the OAuth client credentials file.") from exc
    else:
        raise ConfigurationError(
            "Set GMAIL_CREDENTIALS_PATH or GMAIL_CLIENT_CONFIG_JSON to a Google OAuth "
            "desktop-client configuration."
        )
    try:
        config = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ConfigurationError("The OAuth client configuration is not valid JSON.") from exc
    if (
        not isinstance(config, dict)
        or "web" in config
        or not isinstance(config.get("installed"), dict)
    ):
        raise ConfigurationError("The OAuth configuration must be a desktop client.")
    return config


def gmail_client(credentials: BaseCredentials) -> Any:
    return build("gmail", "v1", credentials=credentials, cache_discovery=False)


def profile(client: Any) -> str:
    result = client.users().getProfile(userId="me").execute()
    email = result.get("emailAddress")
    if not isinstance(email, str) or not email:
        raise ConfigurationError("Gmail did not return an account address.")
    return email


def add_account(path: str | None = None, value: str | None = None) -> str:
    """Authorize one account interactively and save its credentials in Keychain."""
    store = _keyring()
    existing = accounts()
    flow = InstalledAppFlow.from_client_config(client_config(path, value), SCOPES)
    credentials = flow.run_local_server(
        host="127.0.0.1",
        port=0,
        open_browser=True,
        prompt="consent",
        timeout_seconds=180,
        authorization_prompt_message=None,
    )
    if not credentials.refresh_token:
        raise ConfigurationError("Google did not provide a refresh token; authorize again.")
    email = profile(gmail_client(credentials))
    store.set_password(KEYRING_SERVICE, email, credentials.to_json())
    if email not in existing:
        existing.append(email)
        store.set_password(KEYRING_SERVICE, ACCOUNT_INDEX, json.dumps(existing))
    return email


def credentials_for(account: str, *, allow_injected: bool = True) -> Credentials:
    """Use explicitly injected CLI credentials or the named Keychain account."""
    raw = setting("GMAIL_AUTHORIZED_USER_JSON") if allow_injected else None
    if not raw:
        raw = _keyring().get_password(KEYRING_SERVICE, account)
    if not raw:
        raise ConfigurationError(f"No credentials found for account {account}.")
    try:
        info = json.loads(raw)
        if not isinstance(info, dict):
            raise ValueError("Expected an object")
        credentials = Credentials.from_authorized_user_info(info, SCOPES)
    except (ValueError, KeyError) as exc:
        raise ConfigurationError("Authorized-user credentials are invalid.") from exc
    if not credentials.refresh_token:
        raise ConfigurationError("Authorized-user credentials lack a refresh token.")
    return credentials


def export_credentials(account: str) -> Path:
    """Copy one Keychain credential to a private .env for scheduled CLI use."""
    raw = _keyring().get_password(KEYRING_SERVICE, account)
    if not raw:
        raise ConfigurationError(f"No Keychain credentials found for account {account}.")
    path = Path.cwd() / ".env"
    if path.is_symlink():
        raise ConfigurationError("Refusing to write credentials to a symlinked .env.")
    flags = os.O_WRONLY | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags, 0o600)
    try:
        info = os.fstat(descriptor)
        if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid():
            raise ConfigurationError(".env must be a regular file owned by the current user.")
        os.fchmod(descriptor, 0o600)
    finally:
        os.close(descriptor)
    set_key(path, "GMAIL_AUTHORIZED_USER_JSON", raw)
    os.chmod(path, 0o600)
    return path


def connect(account: str, *, allow_injected: bool = True) -> Any:
    client = gmail_client(credentials_for(account, allow_injected=allow_injected))
    actual = profile(client)
    if actual.casefold() != account.casefold():
        raise ConfigurationError(
            f"Credentials belong to {actual}, not requested account {account}; no mail was changed."
        )
    return client


def parse_age(value: str) -> int:
    match = re.fullmatch(r"([1-9][0-9]*)mo", value.strip().lower())
    if not match:
        raise ValueError("Age must be a positive number of months, such as 3mo or 6mo.")
    return int(match.group(1))


@dataclass(frozen=True)
class Mailbox:
    name: str
    months: int | None = None
    before: date | None = None

    def query(self) -> str:
        if self.name not in ("inbox", "archive"):
            raise ValueError("Unknown mailbox.")
        if (self.months is None) == (self.before is None):
            raise ValueError("Choose exactly one age or cutoff date per mailbox.")
        if self.months is not None and self.months < 1:
            raise ValueError("Age must be a positive number of months.")
        if self.months is not None:
            cutoff = f"older_than:{self.months}m"
        else:
            assert self.before is not None
            cutoff = f"before:{self.before.strftime('%Y/%m/%d')}"
        if self.name == "inbox":
            return f"in:inbox {cutoff}"
        return f"-in:inbox -in:sent -in:drafts -in:spam -in:trash {cutoff}"


@dataclass(frozen=True)
class Preview:
    account: str
    matches: dict[str, tuple[str, ...]]
    queries: dict[str, str]

    @property
    def total(self) -> int:
        return len({message for ids in self.matches.values() for message in ids})


def preview(client: Any, account: str, mailboxes: list[Mailbox]) -> Preview:
    if not mailboxes or len({box.name for box in mailboxes}) != len(mailboxes):
        raise ValueError("Select at least one mailbox, without duplicates.")
    matches: dict[str, tuple[str, ...]] = {}
    queries: dict[str, str] = {}
    for box in mailboxes:
        query = box.query()
        queries[box.name] = query
        ids: list[str] = []
        token = None
        while True:
            response = (
                client.users()
                .messages()
                .list(userId="me", q=query, maxResults=500, pageToken=token)
                .execute()
            )
            ids.extend(message["id"] for message in response.get("messages", []))
            token = response.get("nextPageToken")
            if not token:
                break
        matches[box.name] = tuple(dict.fromkeys(ids))
    return Preview(account=account, matches=matches, queries=queries)


class CleanupError(Exception):
    """A cleanup failed after moving zero or more messages."""

    def __init__(self, moved: int) -> None:
        super().__init__(f"Cleanup stopped after moving {moved} messages; inspect Gmail Trash.")
        self.moved = moved


def move_to_trash(client: Any, result: Preview) -> int:
    """Move exactly the IDs in a preview, stopping and reporting on the first failure."""
    ids = list(dict.fromkeys(message for group in result.matches.values() for message in group))
    moved = 0
    for message_id in ids:
        try:
            client.users().messages().trash(userId="me", id=message_id).execute()
        except (HttpError, HttpLib2Error, GoogleAuthError, OSError) as exc:
            raise CleanupError(moved) from exc
        moved += 1
    return moved
