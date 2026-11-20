"""Authentication provider boundary and the loopback-only development provider."""

from __future__ import annotations

import secrets
from dataclasses import dataclass
from typing import Protocol

from gmail_cleanup.gmail.service import ConfigurationError, setting


@dataclass(frozen=True)
class Identity:
    issuer: str
    subject: str
    display_name: str


class AuthProvider(Protocol):
    def authenticate(self, username: str, password: str) -> Identity | None: ...


class LocalDevelopmentProvider:
    """A single configured user, explicitly unsuitable for a shared deployment."""

    def __init__(self, username: str, password: str) -> None:
        if not username or not password:
            raise ConfigurationError("Set GMAIL_DEV_USERNAME and GMAIL_DEV_PASSWORD.")
        self.username = username
        self.password = password

    def authenticate(self, username: str, password: str) -> Identity | None:
        valid_user = secrets.compare_digest(username.encode(), self.username.encode())
        valid_password = secrets.compare_digest(password.encode(), self.password.encode())
        if valid_user and valid_password:
            return Identity("local-development", self.username, self.username)
        return None


def configured_provider() -> AuthProvider:
    provider = setting("GMAIL_AUTH_PROVIDER")
    if provider != "local":
        raise ConfigurationError(
            "Set GMAIL_AUTH_PROVIDER=local for local development; "
            "other providers are not implemented."
        )
    return LocalDevelopmentProvider(
        setting("GMAIL_DEV_USERNAME") or "", setting("GMAIL_DEV_PASSWORD") or ""
    )
