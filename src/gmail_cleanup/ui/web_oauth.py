"""Google web authorization for an already authenticated application user."""

from __future__ import annotations

import json
from pathlib import Path

from google_auth_oauthlib.flow import Flow

from gmail_cleanup.gmail.service import SCOPES, ConfigurationError, setting


def new_flow(redirect_uri: str, *, state: str | None = None, verifier: str | None = None) -> Flow:
    config_path = setting("GMAIL_WEB_CREDENTIALS_PATH")
    if not config_path:
        raise ConfigurationError("The operator must configure GMAIL_WEB_CREDENTIALS_PATH.")
    try:
        config = json.loads(Path(config_path).expanduser().read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ConfigurationError("Cannot read the Google web OAuth client configuration.") from exc
    if not isinstance(config, dict) or not isinstance(config.get("web"), dict):
        raise ConfigurationError("Google OAuth configuration must be a web application client.")
    try:
        return Flow.from_client_config(
            config, scopes=SCOPES, redirect_uri=redirect_uri, state=state,
            code_verifier=verifier, autogenerate_code_verifier=verifier is None,
        )
    except (KeyError, ValueError) as exc:
        raise ConfigurationError("Google web OAuth client configuration is invalid.") from exc
