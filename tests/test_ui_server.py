"""The loopback UI backend: health is open, /api requires the token."""

from __future__ import annotations

from fastapi.testclient import TestClient

from gmail_cleanup.gmail import service
from gmail_cleanup.ui import server


def _client() -> TestClient:
    return TestClient(server.create_app(), base_url="http://127.0.0.1")


def test_health_is_open():
    r = _client().get("/api/health")
    assert r.status_code == 200
    assert r.json() == {"ok": True}


def test_api_requires_session_token():
    assert _client().get("/api/hello").status_code == 401


def test_api_accepts_the_session_token():
    c = _client()
    r = c.get("/api/hello", headers={"x-session-token": server.SESSION_TOKEN})
    assert r.status_code == 200
    assert "message" in r.json()


def test_host_header_is_restricted():
    assert _client().get("/api/health", headers={"host": "evil.example"}).status_code == 400


def test_cleanup_requires_account_bound_one_time_preview(monkeypatch):
    account = "one@example.com"
    other = "two@example.com"
    result = service.Preview(account, {"inbox": ("a",)}, {"inbox": "in:inbox older_than:6m"})
    calls = []
    monkeypatch.setattr(service, "connect", lambda account, **kwargs: account)
    monkeypatch.setattr(service, "preview", lambda client, selected, boxes: result)
    monkeypatch.setattr(
        service, "move_to_trash", lambda client, preview: calls.append(preview) or 1
    )
    c = _client()
    headers = {"x-session-token": server.SESSION_TOKEN}
    request = {"account": account, "mailboxes": [{"name": "inbox", "months": 6}]}
    assert c.post("/api/preview", json=request).status_code == 401
    response = c.post("/api/preview", headers=headers, json=request)
    assert response.status_code == 200
    preview_id = response.json()["preview_id"]
    wrong = c.post(
        "/api/cleanup", headers=headers, json={"account": other, "preview_id": preview_id}
    )
    assert wrong.status_code == 400
    assert calls == []
    response = c.post("/api/preview", headers=headers, json=request)
    preview_id = response.json()["preview_id"]
    cleanup = {"account": account, "preview_id": preview_id}
    assert c.post("/api/cleanup", headers=headers, json=cleanup).json()["moved"] == 1
    assert c.post("/api/cleanup", headers=headers, json=cleanup).status_code == 400
    assert calls == [result]


def test_ui_uses_keychain_not_injected_credentials(monkeypatch):
    called = []
    monkeypatch.setattr(
        service, "connect", lambda account, **kwargs: called.append((account, kwargs))
    )
    response = _client().post(
        "/api/test-connection",
        headers={"x-session-token": server.SESSION_TOKEN},
        json={"account": "one@example.com"},
    )
    assert response.status_code == 200
    assert called == [("one@example.com", {"allow_injected": False})]


def test_invalid_credentials_request_does_not_echo_secret():
    secret = "test-client-secret"
    response = _client().post(
        "/api/config",
        headers={"x-session-token": server.SESSION_TOKEN},
        json={"path": "/test", "value": secret},
    )
    assert response.status_code == 422
    assert secret not in response.text


def test_configuration_status_never_returns_client_secret(monkeypatch):
    secret = "test-client-secret"
    monkeypatch.setattr(
        service, "setting", lambda name: secret if name == "GMAIL_CLIENT_CONFIG_JSON" else None
    )
    response = _client().get(
        "/api/config", headers={"x-session-token": server.SESSION_TOKEN}
    )
    assert response.json() == {"source": "environment or .env value", "path": None}
    assert secret not in response.text


def test_preview_is_expired_after_fifteen_minutes(monkeypatch):
    account = "one@example.com"
    result = service.Preview(account, {"inbox": ("a",)}, {"inbox": "query"})
    monkeypatch.setattr(service, "connect", lambda account, **kwargs: account)
    monkeypatch.setattr(service, "preview", lambda *args: result)
    monkeypatch.setattr(server.time, "monotonic", lambda: 10.0)
    client = _client()
    headers = {"x-session-token": server.SESSION_TOKEN}
    response = client.post(
        "/api/preview", headers=headers,
        json={"account": account, "mailboxes": [{"name": "inbox", "months": 6}]},
    )
    monkeypatch.setattr(server.time, "monotonic", lambda: 911.0)
    response = client.post(
        "/api/cleanup", headers=headers,
        json={"account": account, "preview_id": response.json()["preview_id"]},
    )
    assert response.status_code == 400
    assert "expired" in response.json()["detail"]
