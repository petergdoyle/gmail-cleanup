"""Loopback web-UI backend + launcher (127.0.0.1 only).

A FastAPI app bound to localhost, guarded by a per-session token, serving
the built React UI from ``ui/web`` and exposing the utility's operations
under ``/api``. The backend holds any secrets; the browser never does.
"""

from __future__ import annotations

import secrets
import shutil
import threading
import time
import webbrowser
from datetime import UTC, date, datetime
from pathlib import Path

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from google.auth.exceptions import GoogleAuthError
from google_auth_oauthlib.flow import WSGITimeoutError
from googleapiclient.errors import HttpError
from httplib2 import HttpLib2Error
from keyring.errors import KeyringError
from oauthlib.oauth2 import OAuth2Error
from pydantic import BaseModel, Field, model_validator

from gmail_cleanup.gmail import service

WEB_DIR = Path(__file__).resolve().parent / "web"
# The React source lives at the repo root (ui -> pkg -> src -> root).
WEB_SRC = Path(__file__).resolve().parents[3] / "web-src"
SESSION_TOKEN = secrets.token_urlsafe(16)


class Configuration(BaseModel):
    path: str | None = None
    value: str | None = None

    @model_validator(mode="after")
    def exclusive(self) -> Configuration:
        if bool(self.path) == bool(self.value):
            raise ValueError("Provide either a path or a credential value.")
        return self


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


def create_app() -> FastAPI:
    """Build the loopback app. The UI must build into ui/web first."""
    app = FastAPI(title="gmail_cleanup UI", docs_url=None, redoc_url=None)
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost"])
    config: dict[str, str | None] = {"path": None, "value": None}
    previews: dict[str, tuple[float, service.Preview]] = {}
    preview_lock = threading.Lock()

    @app.exception_handler(RequestValidationError)
    async def validation_error(_request: Request, _exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(status_code=422, content={"detail": "Invalid request."})

    def require_token(x_session_token: str = Header(default="")) -> None:
        if not secrets.compare_digest(x_session_token, SESSION_TOKEN):
            raise HTTPException(status_code=401, detail="bad session token")

    def operation_error(exc: Exception) -> HTTPException:
        if isinstance(exc, (service.ConfigurationError, service.CleanupError, ValueError)):
            return HTTPException(status_code=400, detail=str(exc))
        return HTTPException(
            status_code=502,
            detail="Gmail or Keychain operation failed; check the account and credentials.",
        )

    errors = (
        service.ConfigurationError, service.CleanupError, ValueError, HttpError,
        HttpLib2Error, GoogleAuthError, KeyringError, OAuth2Error, OSError,
        WSGITimeoutError, webbrowser.Error,
    )

    @app.get("/api/health")
    def health() -> JSONResponse:
        """Unauthenticated liveness probe."""
        return JSONResponse({"ok": True})

    @app.get("/api/hello")
    def hello(x_session_token: str = Header(default="")) -> JSONResponse:
        """A sample authenticated operation — replace with the real API."""
        require_token(x_session_token)
        return JSONResponse({"message": "hello from the backend"})

    @app.get("/api/accounts", dependencies=[Depends(require_token)])
    def get_accounts() -> dict[str, list[str]]:
        try:
            return {"accounts": service.accounts()}
        except errors as exc:
            raise operation_error(exc) from exc

    @app.post("/api/accounts", dependencies=[Depends(require_token)])
    def add_account() -> dict[str, str]:
        try:
            return {"account": service.add_account(path=config["path"], value=config["value"])}
        except errors as exc:
            raise operation_error(exc) from exc

    @app.post("/api/config", dependencies=[Depends(require_token)])
    def configure(body: Configuration) -> dict[str, bool]:
        try:
            service.client_config(path=body.path, value=body.value)
        except errors as exc:
            raise operation_error(exc) from exc
        config.update(path=body.path, value=body.value)
        return {"ok": True}

    @app.get("/api/config", dependencies=[Depends(require_token)])
    def get_configuration() -> dict[str, str | None]:
        if config["value"] is not None:
            return {"source": "session value", "path": None}
        if config["path"] is not None:
            return {"source": "session path", "path": config["path"]}
        if service.setting("GMAIL_CLIENT_CONFIG_JSON"):
            return {"source": "environment or .env value", "path": None}
        path = service.setting("GMAIL_CREDENTIALS_PATH")
        return {"source": "environment or .env path" if path else "not configured", "path": path}

    @app.post("/api/test-connection", dependencies=[Depends(require_token)])
    def test_connection(body: AccountRequest) -> dict[str, str]:
        try:
            service.connect(body.account, allow_injected=False)
            return {
                "account": body.account,
                "status": "connected",
                "tested_at": datetime.now(UTC).isoformat(),
            }
        except errors as exc:
            raise operation_error(exc) from exc

    @app.post("/api/preview", dependencies=[Depends(require_token)])
    def preview(body: PreviewRequest) -> dict:
        try:
            boxes = [
                service.Mailbox(item.name, item.months, item.before) for item in body.mailboxes
            ]
            client = service.connect(body.account, allow_injected=False)
            result = service.preview(client, body.account, boxes)
        except errors as exc:
            raise operation_error(exc) from exc
        preview_id = secrets.token_urlsafe(32)
        now = time.monotonic()
        with preview_lock:
            previews.clear()
            previews[preview_id] = (now, result)
        return {
            "preview_id": preview_id,
            "account": result.account,
            "counts": {name: len(ids) for name, ids in result.matches.items()},
            "queries": result.queries,
            "total": result.total,
        }

    @app.post("/api/cleanup", dependencies=[Depends(require_token)])
    def cleanup(body: CleanupRequest) -> dict[str, int | str]:
        with preview_lock:
            entry = previews.pop(body.preview_id, None)
        if entry is None or time.monotonic() - entry[0] > 900:
            raise HTTPException(
                status_code=400, detail="Preview expired or already used; preview again."
            )
        result = entry[1]
        if result.account != body.account:
            raise HTTPException(status_code=400, detail="Preview belongs to another account.")
        try:
            client = service.connect(result.account, allow_injected=False)
            moved = service.move_to_trash(client, result)
            return {
                "account": result.account,
                "moved": moved,
                "completed_at": datetime.now(UTC).isoformat(),
            }
        except errors as exc:
            raise operation_error(exc) from exc

    if WEB_DIR.is_dir():
        @app.get("/", response_class=HTMLResponse)
        def index() -> HTMLResponse:
            html = (WEB_DIR / "index.html").read_text(encoding="utf-8")
            bootstrap = f'<script>window.__GMAIL_SESSION_TOKEN__="{SESSION_TOKEN}";</script>'
            return HTMLResponse(html.replace("</head>", bootstrap + "</head>", 1))

        app.mount("/", StaticFiles(directory=WEB_DIR, html=True), name="web")

    return app


def _ui_built() -> bool:
    return WEB_DIR.is_dir() and any(WEB_DIR.iterdir())


def ensure_built() -> bool:
    """Make sure the UI is built, building it if needed.

    - Already built (e.g. served from an installed wheel) -> True, no work.
    - Not built but the React source (web-src/) is present (a dev checkout)
      -> run the npm build, then True. So `gmail_cleanup ui` just works.
    - Not built and no web-src/ (a broken wheel) -> False (caller errors).
    """
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
    """Build-if-needed and serve the loopback UI in the foreground (Ctrl-C to stop).

    Opens the browser once the server is up (unless open_browser is False).
    """
    import uvicorn

    built = ensure_built()
    if not built:
        raise SystemExit(
            "The packaged UI is missing and could not be built. If you installed\n"
            "this as a tool, reinstall it; in a source checkout, run 'make web'."
        )
    url = f"http://{host}:{port}"
    print(f"  gmail_cleanup ui  ->  {url}")
    print("  127.0.0.1 only. Press Ctrl-C to stop.")
    if open_browser:
        import threading
        import webbrowser

        threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    uvicorn.run(create_app(), host=host, port=port, log_level="warning")
