"""Verify the development identity boundary and scoped persistent storage."""

import sqlite3

import pytest
from cryptography.fernet import Fernet

from gmail_cleanup.gmail.service import ConfigurationError
from gmail_cleanup.ui import auth, web_oauth
from gmail_cleanup.ui.auth import Identity, LocalDevelopmentProvider
from gmail_cleanup.ui.store import Store


def test_local_authentication_requires_matching_configured_credentials():
    provider = LocalDevelopmentProvider("alice", "test-password")
    assert provider.authenticate("alice", "wrong") is None
    assert provider.authenticate("wrong", "test-password") is None
    assert provider.authenticate("alice", "test-password") == Identity(
        "local-development", "alice", "alice"
    )
    with pytest.raises(ConfigurationError):
        LocalDevelopmentProvider("", "")


def test_store_isolates_users_and_encrypts_tokens(tmp_path):
    key = Fernet.generate_key().decode()
    path = tmp_path / "settings.sqlite"
    alice = Identity("issuer", "alice", "Alice")
    bob = Identity("issuer", "bob", "Bob")
    other_issuer = Identity("other-issuer", "alice", "Alice")
    store = Store(path, key)
    store.save_account(alice, "a@example.com", '{"refresh_token":"test-secret"}')
    store.put(alice, "theme", "dark")
    assert store.list_accounts(bob) == []
    assert store.get(bob, "theme", "light") == "light"
    assert store.list_accounts(other_issuer) == []
    assert store.get(other_issuer, "theme", "light") == "light"
    with pytest.raises(ConfigurationError, match="not connected"):
        store.credentials(bob, "a@example.com")
    with sqlite3.connect(path) as db:
        token = db.execute("SELECT credentials FROM accounts").fetchone()[0]
        assert b"test-secret" not in token
    reloaded = Store(path, key)
    assert reloaded.get(alice, "theme", "light") == "dark"
    assert "test-secret" in reloaded.credentials(alice, "a@example.com")
    with pytest.raises(ConfigurationError, match="decrypt"):
        Store(path, Fernet.generate_key().decode()).credentials(alice, "a@example.com")


def test_provider_requires_explicit_supported_configuration(monkeypatch):
    settings = {}
    monkeypatch.setattr(auth, "setting", settings.get)
    with pytest.raises(ConfigurationError, match="GMAIL_AUTH_PROVIDER"):
        auth.configured_provider()
    settings["GMAIL_AUTH_PROVIDER"] = "authentik"
    with pytest.raises(ConfigurationError, match="other providers"):
        auth.configured_provider()
    settings["GMAIL_AUTH_PROVIDER"] = "local"
    with pytest.raises(ConfigurationError, match="GMAIL_DEV_USERNAME"):
        auth.configured_provider()


def test_web_oauth_client_configuration_and_pkce(tmp_path, monkeypatch):
    path = tmp_path / "client.json"
    monkeypatch.setattr(web_oauth, "setting", lambda name: str(path))
    path.write_text('{"installed": {}}', encoding="utf-8")
    with pytest.raises(ConfigurationError, match="web application"):
        web_oauth.new_flow("http://127.0.0.1:8100/oauth/google/callback")
    path.write_text('{"web": {}}', encoding="utf-8")
    with pytest.raises(ConfigurationError, match="invalid"):
        web_oauth.new_flow("http://127.0.0.1:8100/oauth/google/callback")
    path.write_text(
        '{"web": {"client_id": "test", "client_secret": "test",'
        ' "auth_uri": "https://example.com/auth",'
        ' "token_uri": "https://example.com/token"}}',
        encoding="utf-8",
    )
    flow = web_oauth.new_flow("http://127.0.0.1:8100/oauth/google/callback")
    url, state = flow.authorization_url(access_type="offline")
    assert state
    assert flow.code_verifier
    assert "code_challenge=" in url
    assert "code_challenge_method=S256" in url
