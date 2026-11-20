"""Verify local sessions, user isolation and account-bound cleanup."""

import json
from unittest.mock import Mock

import pytest
from cryptography.fernet import Fernet
from fastapi.testclient import TestClient

from gmail_cleanup.gmail import service
from gmail_cleanup.ui import server
from gmail_cleanup.ui.auth import Identity, LocalDevelopmentProvider
from gmail_cleanup.ui.store import Store


@pytest.fixture
def application(tmp_path):
    store = Store(tmp_path / "settings.sqlite", Fernet.generate_key().decode())
    provider = LocalDevelopmentProvider("alice", "test-password")
    app = server.create_app(provider, store)
    return app, store


def client(app):
    return TestClient(app, base_url="http://127.0.0.1")


def login(c):
    result = c.post(
        "/api/login",
        headers={"x-bootstrap-token": server.BOOTSTRAP_TOKEN},
        json={"username": "alice", "password": "test-password"},
    )
    assert result.status_code == 200
    return {"x-csrf-token": result.json()["csrf"]}


def test_login_logout_csrf_and_host_restriction(application):
    app, _ = application
    c = client(app)
    assert c.get("/api/health").json() == {"ok": True}
    assert c.get("/api/health", headers={"host": "evil.example"}).status_code == 400
    assert c.get("/api/accounts").status_code == 401
    assert c.post("/api/login", json={"username": "alice", "password": "bad"}).status_code == 403
    assert c.post(
        "/api/login", headers={"x-bootstrap-token": server.BOOTSTRAP_TOKEN},
        json={"username": "alice", "password": "bad"},
    ).status_code == 401
    headers = login(c)
    assert c.get("/api/session").json()["user"] == "alice"
    assert c.post("/api/settings/theme", json={"theme": "dark"}).status_code == 403
    assert c.post("/api/settings/theme", headers=headers, json={"theme": "dark"}).status_code == 200
    assert c.post("/api/logout", headers=headers).status_code == 200
    assert c.get("/api/session").status_code == 401


def test_settings_persist_and_account_data_is_user_scoped(application):
    app, store = application
    alice = Identity("local-development", "alice", "alice")
    bob = Identity("local-development", "bob", "bob")
    store.save_account(alice, "a@example.com", '{"refresh_token":"fake"}')
    store.save_account(bob, "b@example.com", '{"refresh_token":"fake"}')
    c = client(app)
    headers = login(c)
    assert c.get("/api/accounts").json()["accounts"] == ["a@example.com"]
    assert c.post(
        "/api/accounts/remove", headers=headers, json={"account": "b@example.com"}
    ).status_code != 200
    assert store.list_accounts(bob) == ["b@example.com"]
    assert c.post("/api/settings/theme", headers=headers, json={"theme": "dark"}).status_code == 200
    assert c.get("/api/settings").json()["theme"] == "dark"
    assert c.post("/api/logout", headers=headers).status_code == 200
    login(c)
    assert c.get("/api/settings").json()["theme"] == "dark"


def test_cleanup_preview_is_bound_to_login_session(application, monkeypatch):
    app, store = application
    user = Identity("local-development", "alice", "alice")
    info = {"token": "fake", "refresh_token": "fake", "token_uri": "https://example.com",
            "client_id": "fake", "client_secret": "fake"}
    store.save_account(user, "a@example.com", json.dumps(info))
    result = service.Preview("a@example.com", {"inbox": ("a",)}, {"inbox": "query"})
    monkeypatch.setattr(service, "gmail_client", lambda credentials: Mock())
    monkeypatch.setattr(service, "profile", lambda client: "a@example.com")
    monkeypatch.setattr(service, "preview", lambda *args: result)
    moved = Mock(return_value=1)
    monkeypatch.setattr(service, "move_to_trash", moved)
    first, second = client(app), client(app)
    headers, other_headers = login(first), login(second)
    preview = first.post(
        "/api/preview", headers=headers,
        json={"account": "a@example.com", "mailboxes": [{"name": "inbox", "months": 6}]},
    ).json()
    request = {"account": "a@example.com", "preview_id": preview["preview_id"]}
    assert second.post("/api/cleanup", headers=other_headers, json=request).status_code == 400
    wrong = {"account": "other@example.com", "preview_id": preview["preview_id"]}
    assert first.post("/api/cleanup", headers=headers, json=wrong).status_code == 400
    preview = first.post(
        "/api/preview", headers=headers,
        json={"account": "a@example.com", "mailboxes": [{"name": "inbox", "months": 6}]},
    ).json()
    request["preview_id"] = preview["preview_id"]
    assert first.post("/api/cleanup", headers=headers, json=request).json()["moved"] == 1
    assert first.post("/api/cleanup", headers=headers, json=request).status_code == 400
    moved.assert_called_once()


def test_google_oauth_state_and_session_are_required(application, monkeypatch):
    app, store = application
    flow = Mock()
    flow.code_verifier = "verifier"
    flow.authorization_url.return_value = ("https://accounts.google.com/test", "state")
    flow.credentials.refresh_token = "fake"
    flow.credentials.to_json.return_value = '{"refresh_token":"fake"}'
    monkeypatch.setattr(server.web_oauth, "new_flow", lambda *args, **kwargs: flow)
    monkeypatch.setattr(service, "gmail_client", lambda credentials: Mock())
    monkeypatch.setattr(service, "profile", lambda client: "a@example.com")
    c = client(app)
    headers = login(c)
    assert c.post("/api/accounts/connect", headers=headers).status_code == 200
    assert c.get("/oauth/google/callback?state=wrong&code=x").status_code == 400
    assert store.list_accounts(Identity("local-development", "alice", "alice")) == []
    c.post("/api/accounts/connect", headers=headers)
    response = c.get("/oauth/google/callback?state=state&code=x", follow_redirects=False)
    assert response.status_code == 303
    assert store.list_accounts(Identity("local-development", "alice", "alice")) == ["a@example.com"]
    assert c.get("/oauth/google/callback?state=state&code=x").status_code == 400


def test_preview_expiration(application, monkeypatch):
    app, store = application
    user = Identity("local-development", "alice", "alice")
    info = {"token": "fake", "refresh_token": "fake", "token_uri": "https://example.com",
            "client_id": "fake", "client_secret": "fake"}
    store.save_account(user, "a@example.com", json.dumps(info))
    result = service.Preview("a@example.com", {"inbox": ("a",)}, {"inbox": "query"})
    monkeypatch.setattr(service, "gmail_client", lambda credentials: Mock())
    monkeypatch.setattr(service, "profile", lambda client: "a@example.com")
    monkeypatch.setattr(service, "preview", lambda *args: result)
    moved = Mock()
    monkeypatch.setattr(service, "move_to_trash", moved)
    c = client(app)
    headers = login(c)
    preview = c.post(
        "/api/preview", headers=headers,
        json={"account": "a@example.com", "mailboxes": [{"name": "inbox", "months": 6}]},
    ).json()
    monkeypatch.setattr(server, "PREVIEW_SECONDS", 0)
    assert c.post(
        "/api/cleanup", headers=headers,
        json={"account": "a@example.com", "preview_id": preview["preview_id"]},
    ).status_code == 400
    moved.assert_not_called()


def test_google_oauth_expiration(application, monkeypatch):
    app, store = application
    flow = Mock()
    flow.code_verifier = "verifier"
    flow.authorization_url.return_value = ("https://accounts.google.com/test", "state")
    monkeypatch.setattr(server.web_oauth, "new_flow", lambda *args, **kwargs: flow)
    c = client(app)
    headers = login(c)
    c.post("/api/accounts/connect", headers=headers)
    monkeypatch.setattr(server, "OAUTH_SECONDS", 0)
    assert c.get("/oauth/google/callback?state=state&code=x").status_code == 400
    flow.fetch_token.assert_not_called()
    assert store.list_accounts(Identity("local-development", "alice", "alice")) == []


def test_session_rotation_and_expiry(application, monkeypatch):
    app, _ = application
    c = client(app)
    login(c)
    previous_cookie = c.cookies.get(server.SESSION_COOKIE)
    login(c)
    previous = client(app)
    previous.cookies.set(server.SESSION_COOKIE, previous_cookie)
    assert previous.get("/api/session").status_code == 401
    monkeypatch.setattr(server, "SESSION_SECONDS", 0)
    login(c)
    assert c.get("/api/session").status_code == 401


def test_account_preferences_are_validated_and_scoped(application):
    app, store = application
    alice = Identity("local-development", "alice", "alice")
    bob = Identity("local-development", "bob", "bob")
    store.save_account(alice, "a@example.com", '{"refresh_token":"fake"}')
    store.save_account(bob, "b@example.com", '{"refresh_token":"fake"}')
    c = client(app)
    headers = login(c)
    preferences = {
        "account": "a@example.com",
        "inbox": {"selected": True, "months": 6, "before": None},
        "archive": {"selected": False, "months": 3, "before": "2025-01-01"},
    }
    assert c.post("/api/settings/account", headers=headers, json=preferences).status_code == 200
    assert c.get("/api/settings").json()["accounts"]["a@example.com"] == {
        key: preferences[key] for key in ("inbox", "archive")
    }
    preferences["account"] = "b@example.com"
    assert c.post("/api/settings/account", headers=headers, json=preferences).status_code == 400
    assert store.get(bob, "account:b@example.com", None) is None
    preferences["account"] = "a@example.com"
    preferences["inbox"]["months"] = 0
    assert c.post("/api/settings/account", headers=headers, json=preferences).status_code == 422


def test_google_oauth_cancellation_missing_code_and_missing_refresh(application, monkeypatch):
    app, store = application
    flow = Mock()
    flow.code_verifier = "verifier"
    flow.authorization_url.return_value = ("https://accounts.google.com/test", "state")
    flow.credentials.refresh_token = None
    monkeypatch.setattr(server.web_oauth, "new_flow", lambda *args, **kwargs: flow)
    c = client(app)
    headers = login(c)
    c.post("/api/accounts/connect", headers=headers)
    response = c.get(
        "/oauth/google/callback?state=state&error=access_denied", follow_redirects=False
    )
    assert response.status_code == 303
    assert response.headers["location"] == "/?google=denied"
    c.post("/api/accounts/connect", headers=headers)
    assert c.get("/oauth/google/callback?state=state").status_code == 400
    c.post("/api/accounts/connect", headers=headers)
    response = c.get("/oauth/google/callback?state=state&code=secret-code")
    assert response.status_code == 400
    assert "secret-code" not in response.text
    assert store.list_accounts(Identity("local-development", "alice", "alice")) == []
