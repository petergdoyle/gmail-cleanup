"""Loopback web-UI backend + launcher (127.0.0.1 only).

A FastAPI app bound to localhost, guarded by a per-session token, serving
the built React UI from ``ui/web`` and exposing the utility's operations
under ``/api``. The backend holds any secrets; the browser never does.
"""

from __future__ import annotations

import secrets
import shutil
from pathlib import Path

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

WEB_DIR = Path(__file__).resolve().parent / "web"
# The React source lives at the repo root (ui -> pkg -> src -> root).
WEB_SRC = Path(__file__).resolve().parents[3] / "web-src"
SESSION_TOKEN = secrets.token_urlsafe(16)


def create_app() -> FastAPI:
    """Build the loopback app. The UI must build into ui/web first."""
    app = FastAPI(title="gmail_cleanup UI", docs_url=None, redoc_url=None)

    def require_token(x_session_token: str = Header(default="")) -> None:
        if not secrets.compare_digest(x_session_token, SESSION_TOKEN):
            raise HTTPException(status_code=401, detail="bad session token")

    @app.get("/api/health")
    def health() -> JSONResponse:
        """Unauthenticated liveness probe."""
        return JSONResponse({"ok": True})

    @app.get("/api/hello")
    def hello(x_session_token: str = Header(default="")) -> JSONResponse:
        """A sample authenticated operation — replace with the real API."""
        require_token(x_session_token)
        return JSONResponse({"message": "hello from the backend"})

    if WEB_DIR.is_dir():
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
    print(f"  session token (injected into the page): {SESSION_TOKEN[:8]}...")
    print("  127.0.0.1 only. Press Ctrl-C to stop.")
    if open_browser:
        import threading
        import webbrowser

        threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    uvicorn.run(create_app(), host=host, port=port, log_level="warning")
