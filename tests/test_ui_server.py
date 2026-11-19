"""The loopback UI backend: health is open, /api requires the token."""

from __future__ import annotations

from fastapi.testclient import TestClient

from gmail_cleanup.ui import server


def _client() -> TestClient:
    return TestClient(server.create_app())


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
