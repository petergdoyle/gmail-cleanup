"""Loopback-only development UI with user-bound sessions and Gmail accounts."""

from __future__ import annotations

import json
import secrets
import shutil
import threading
import time
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit, urlunsplit

from fastapi import Depends, FastAPI, Header, HTTPException, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from google.auth.exceptions import GoogleAuthError
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError
from httplib2 import HttpLib2Error
from oauthlib.oauth2 import OAuth2Error
from pydantic import BaseModel, Field

from gmail_cleanup.gmail import service
from gmail_cleanup.ui import web_oauth
from gmail_cleanup.ui.auth import AuthProvider, Identity, configured_provider
from gmail_cleanup.ui.store import Store

WEB_DIR = Path(__file__).resolve().parent / "web"
WEB_SRC = Path(__file__).resolve().parents[3] / "web-src"
BOOTSTRAP_TOKEN = secrets.token_urlsafe(32)
SESSION_COOKIE = "gmail_cleanup_session"
SESSION_SECONDS = 8 * 60 * 60
OAUTH_SECONDS = 10 * 60
PREVIEW_SECONDS = 15 * 60


@dataclass
class Session:
    user: Identity
    csrf: str
    expires: float
    oauth: dict[str, Any] | None = None
    previews: dict[str, tuple[float, service.Preview]] = field(default_factory=dict)


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=256)
    password: str = Field(min_length=1, max_length=1024)


class AccountRequest(BaseModel):
    account: str = Field(min_length=1)


class BoxRequest(BaseModel):
    name: str
    months: int | None = Field(default=None, ge=1)
    before: date | None = None


class PreviewRequest(AccountRequest):
    mailboxes: list[BoxRequest]


class CleanupRequest(AccountRequest):
    preview_id: str = Field(min_length=1)


class BoxSettings(BaseModel):
    selected: bool
    months: int = Field(ge=1)
    before: date | None = None


class AccountSettings(AccountRequest):
    inbox: BoxSettings
    archive: BoxSettings


class ThemeRequest(BaseModel):
    theme: str


def create_app(provider: AuthProvider | None = None, store: Store | None = None) -> FastAPI:
    """Create the local UI; configuration errors are surfaced on startup."""
    provider = provider or configured_provider()
    if store is None:
        key = service.setting("GMAIL_ENCRYPTION_KEY")
        if not key:
            raise service.ConfigurationError("Set GMAIL_ENCRYPTION_KEY before starting the UI.")
        store = Store(Path.cwd() / ".run" / "settings.sqlite", key)
    app = FastAPI(title="gmail_cleanup UI", docs_url=None, redoc_url=None)
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost"])
    sessions: dict[str, Session] = {}
    lock = threading.RLock()

    @app.exception_handler(RequestValidationError)
    async def validation_error(_request: Request, _exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(status_code=422, content={"detail": "Invalid request."})

    @app.exception_handler(service.ConfigurationError)
    async def configuration_error(
        _request: Request, exc: service.ConfigurationError
    ) -> JSONResponse:
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    def authenticated(request: Request) -> Session:
        key = request.cookies.get(SESSION_COOKIE, "")
        with lock:
            session = sessions.get(key)
            if session is None or session.expires <= time.monotonic():
                sessions.pop(key, None)
                raise HTTPException(status_code=401, detail="Sign in required.")
            if request.method not in ("GET", "HEAD"):
                csrf = request.headers.get("x-csrf-token", "")
                if not secrets.compare_digest(csrf, session.csrf):
                    raise HTTPException(status_code=403, detail="Invalid request token.")
            return session

    def client_for(user: Identity, email: str) -> Any:
        raw = store.credentials(user, email)
        try:
            credentials = Credentials.from_authorized_user_info(json.loads(raw), service.SCOPES)
        except (ValueError, KeyError, TypeError) as exc:
            raise service.ConfigurationError(
                "Saved Google credentials are invalid; reconnect the account."
            ) from exc
        client = service.gmail_client(credentials)
        actual = service.profile(client)
        if actual.casefold() != email.casefold():
            raise service.ConfigurationError(
                "Connected Google account does not match the selection."
            )
        return client

    def fail(exc: Exception) -> HTTPException:
        if isinstance(exc, (service.ConfigurationError, service.CleanupError, ValueError)):
            return HTTPException(status_code=400, detail=str(exc))
        return HTTPException(
            status_code=502, detail="Google operation failed; check the connection."
        )

    errors = (service.ConfigurationError, service.CleanupError, ValueError,
              HttpError, HttpLib2Error, GoogleAuthError, OAuth2Error, OSError)

    @app.get("/api/health")
    def health() -> dict[str, bool]:
        return {"ok": True}

    @app.post("/api/login")
    def login(
        body: LoginRequest, request: Request, response: Response,
        x_bootstrap_token: str = Header(default=""),
    ):
        if not secrets.compare_digest(x_bootstrap_token, BOOTSTRAP_TOKEN):
            raise HTTPException(status_code=403, detail="Invalid request token.")
        user = provider.authenticate(body.username, body.password)
        if user is None:
            raise HTTPException(status_code=401, detail="Invalid username or password.")
        key = secrets.token_urlsafe(32)
        session = Session(user, secrets.token_urlsafe(32), time.monotonic() + SESSION_SECONDS)
        with lock:
            sessions.pop(request.cookies.get(SESSION_COOKIE, ""), None)
            sessions[key] = session
        response.set_cookie(
            SESSION_COOKIE, key, httponly=True, samesite="lax", max_age=SESSION_SECONDS, path="/"
        )
        return {"user": user.display_name, "csrf": session.csrf}

    @app.get("/api/session")
    def current_session(session: Session = Depends(authenticated)) -> dict[str, str]:
        return {"user": session.user.display_name, "csrf": session.csrf}

    @app.post("/api/logout")
    def logout(request: Request, response: Response, session: Session = Depends(authenticated)):
        with lock:
            sessions.pop(request.cookies.get(SESSION_COOKIE, ""), None)
        response.delete_cookie(SESSION_COOKIE, path="/")
        return {"ok": True}

    @app.get("/api/accounts")
    def get_accounts(session: Session = Depends(authenticated)):
        return {"accounts": store.list_accounts(session.user)}

    @app.post("/api/accounts/connect")
    def begin_google(request: Request, session: Session = Depends(authenticated)):
        try:
            redirect = str(request.base_url).rstrip("/") + "/oauth/google/callback"
            flow = web_oauth.new_flow(redirect)
            url, state = flow.authorization_url(access_type="offline", prompt="consent")
            with lock:
                session.oauth = {
                    "state": state, "verifier": flow.code_verifier,
                    "redirect": redirect, "created": time.monotonic(),
                }
            return {"url": url}
        except web_oauth.WebOAuthConfigurationError as exc:
            return JSONResponse(
                status_code=400,
                content={"detail": str(exc), "code": "google_web_client_configuration"},
            )
        except errors as exc:
            raise fail(exc) from exc

    @app.get("/oauth/google/callback")
    def google_callback(request: Request, session: Session = Depends(authenticated)):
        with lock:
            transaction, session.oauth = session.oauth, None
        state = request.query_params.get("state", "")
        if (
            not transaction or time.monotonic() - transaction["created"] > OAUTH_SECONDS
            or not secrets.compare_digest(state, transaction["state"])
        ):
            raise HTTPException(status_code=400, detail="Google authorization expired or invalid.")
        if request.query_params.get("error"):
            return RedirectResponse("/?google=denied", status_code=303)
        if not request.query_params.get("code"):
            raise HTTPException(status_code=400, detail="Google authorization returned no code.")
        try:
            flow = web_oauth.new_flow(
                transaction["redirect"], state=state, verifier=transaction["verifier"]
            )
            parts = urlsplit(str(request.url))
            authorization_response = urlunsplit(
                ("https", parts.netloc, parts.path, parts.query, parts.fragment)
            )
            flow.fetch_token(authorization_response=authorization_response)
            credentials = flow.credentials
            if not credentials.refresh_token:
                raise service.ConfigurationError("Google did not provide a refresh token.")
            email = service.profile(service.gmail_client(credentials))
            store.save_account(session.user, email, credentials.to_json())
        except errors as exc:
            raise fail(exc) from exc
        return RedirectResponse("/?google=connected", status_code=303)

    @app.post("/api/accounts/remove")
    def remove_account(body: AccountRequest, session: Session = Depends(authenticated)):
        store.credentials(session.user, body.account)
        store.delete_account(session.user, body.account)
        with lock:
            session.previews.clear()
        return {"ok": True}

    @app.get("/api/settings")
    def settings(session: Session = Depends(authenticated)):
        accounts = store.list_accounts(session.user)
        return {
            "theme": store.get(session.user, "theme", "light"),
            "accounts": {
                email: store.get(session.user, f"account:{email}", None) for email in accounts
            },
        }

    @app.post("/api/settings/theme")
    def save_theme(body: ThemeRequest, session: Session = Depends(authenticated)):
        if body.theme not in ("light", "dark"):
            raise HTTPException(status_code=400, detail="Choose light or dark.")
        store.put(session.user, "theme", body.theme)
        return {"ok": True}

    @app.post("/api/settings/account")
    def save_settings(body: AccountSettings, session: Session = Depends(authenticated)):
        store.credentials(session.user, body.account)
        data = {
            "inbox": body.inbox.model_dump(mode="json"),
            "archive": body.archive.model_dump(mode="json"),
        }
        store.put(session.user, f"account:{body.account}", data)
        return {"ok": True}

    @app.post("/api/test-connection")
    def test_connection(body: AccountRequest, session: Session = Depends(authenticated)):
        try:
            client_for(session.user, body.account)
            return {"account": body.account, "status": "connected",
                    "tested_at": datetime.now(UTC).isoformat()}
        except errors as exc:
            raise fail(exc) from exc

    @app.post("/api/preview")
    def preview(body: PreviewRequest, session: Session = Depends(authenticated)):
        try:
            boxes = [
                service.Mailbox(item.name, item.months, item.before) for item in body.mailboxes
            ]
            result = service.preview(client_for(session.user, body.account), body.account, boxes)
        except errors as exc:
            raise fail(exc) from exc
        preview_id = secrets.token_urlsafe(32)
        with lock:
            session.previews.clear()
            session.previews[preview_id] = (time.monotonic(), result)
        return {"preview_id": preview_id, "account": result.account,
                "counts": {name: len(ids) for name, ids in result.matches.items()},
                "queries": result.queries, "total": result.total}

    @app.post("/api/cleanup")
    def cleanup(body: CleanupRequest, session: Session = Depends(authenticated)):
        with lock:
            entry = session.previews.pop(body.preview_id, None)
        if entry is None or time.monotonic() - entry[0] > PREVIEW_SECONDS:
            raise HTTPException(
                status_code=400, detail="Preview expired or already used; preview again."
            )
        result = entry[1]
        if result.account != body.account:
            raise HTTPException(status_code=400, detail="Preview belongs to another account.")
        try:
            moved = service.move_to_trash(client_for(session.user, result.account), result)
            return {"account": result.account, "moved": moved,
                    "completed_at": datetime.now(UTC).isoformat()}
        except errors as exc:
            raise fail(exc) from exc

    if WEB_DIR.is_dir():
        @app.get("/", response_class=HTMLResponse)
        def index():
            html = (WEB_DIR / "index.html").read_text(encoding="utf-8")
            bootstrap = f'<script>window.__GMAIL_BOOTSTRAP_TOKEN__="{BOOTSTRAP_TOKEN}";</script>'
            return HTMLResponse(html.replace("</head>", bootstrap + "</head>", 1),
                                headers={"Cache-Control": "no-store"})

        app.mount("/", StaticFiles(directory=WEB_DIR, html=True), name="web")
    return app


def _ui_built() -> bool:
    return WEB_DIR.is_dir() and any(WEB_DIR.iterdir())


def ensure_built() -> bool:
    import subprocess

    if _ui_built():
        return True
    if not WEB_SRC.is_dir():
        return False
    if shutil.which("npm") is None:
        print("UI not built and npm is not installed — install Node first.")
        return False
    print("Building the UI (first run) — this can take a moment...")
    subprocess.run(["npm", "install"], cwd=WEB_SRC, check=True)
    subprocess.run(["npm", "run", "build"], cwd=WEB_SRC, check=True)
    return _ui_built()


def serve(host: str = "127.0.0.1", port: int = 8100, open_browser: bool = True) -> None:
    import uvicorn

    if host not in ("127.0.0.1", "localhost"):
        raise SystemExit("The development authentication provider is loopback-only.")
    if not ensure_built():
        raise SystemExit("The packaged UI is missing. In a source checkout, run 'make web'.")
    app = create_app()
    url = f"http://{host}:{port}"
    print(f"  gmail_cleanup ui  ->  {url}")
    print("  Local development authentication only. Press Ctrl-C to stop.")
    if open_browser:
        import webbrowser

        threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    uvicorn.run(app, host=host, port=port, log_level="warning")
