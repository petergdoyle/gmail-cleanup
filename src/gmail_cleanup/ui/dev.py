"""Manage the local development UI without touching unrelated processes."""

from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path

RUN_DIR = Path.cwd() / ".run"
PID_FILE = RUN_DIR / "gmail-ui.json"
URL = "http://127.0.0.1:8100"
PROCESS_MARKER = "-m gmail_cleanup.ui.dev --serve"


def process_details(pid: int) -> str:
    result = subprocess.run(
        ["ps", "-p", str(pid), "-o", "lstart=", "-o", "command="],
        capture_output=True, text=True, check=False,
    )
    return result.stdout.strip()


def managed_process() -> tuple[int, str] | None:
    if not PID_FILE.exists():
        return None
    try:
        data = json.loads(PID_FILE.read_text(encoding="utf-8"))
        pid, details = data["pid"], data["details"]
        if not isinstance(pid, int) or pid <= 1 or not isinstance(details, str):
            raise ValueError("Invalid process record")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise SystemExit("Invalid .run/gmail-ui.json; inspect it before proceeding.") from exc
    current = process_details(pid)
    if not current:
        return None
    if current != details or PROCESS_MARKER not in current:
        raise SystemExit("Recorded PID belongs to another process; inspect .run/gmail-ui.json.")
    return pid, current


def responsive() -> bool:
    try:
        with urllib.request.urlopen(f"{URL}/api/health", timeout=1) as response:
            return response.status == 200 and json.load(response) == {"ok": True}
    except (OSError, urllib.error.URLError, ValueError):
        return False


def open_browser() -> None:
    try:
        opened = webbrowser.open(URL)
    except webbrowser.Error as exc:
        print(f"Could not open a browser: {exc}. Open {URL} manually.")
        return
    if not opened:
        print(f"Could not open a browser. Open {URL} manually.")


def start() -> None:
    current = managed_process()
    if current:
        if not responsive():
            raise SystemExit(f"Managed process {current[0]} is not responding at {URL}.")
        print(f"Development UI already running at {URL} (PID {current[0]}).")
        open_browser()
        return
    if responsive():
        raise SystemExit(f"A service already responds at {URL}; it was not started by this tool.")
    RUN_DIR.mkdir(mode=0o700, exist_ok=True)
    with (RUN_DIR / "gmail-ui.log").open("a", encoding="utf-8") as log:
        process = subprocess.Popen(
            [sys.executable, "-m", "gmail_cleanup.ui.dev", "--serve"],
            stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
            start_new_session=True,
        )
    details = process_details(process.pid)
    PID_FILE.write_text(json.dumps({"pid": process.pid, "details": details}), encoding="utf-8")
    for _ in range(300):
        if process.poll() is not None:
            PID_FILE.unlink(missing_ok=True)
            raise SystemExit("Development UI exited during startup; see .run/gmail-ui.log.")
        if responsive():
            print(f"Development UI running at {URL} (PID {process.pid}).")
            open_browser()
            return
        time.sleep(0.1)
    raise SystemExit("Development UI is not ready; check .run/gmail-ui.log and dev-status.")


def stop() -> None:
    current = managed_process()
    if current is None:
        PID_FILE.unlink(missing_ok=True)
        print("Development UI is not running.")
        return
    pid, details = current
    os.kill(pid, signal.SIGTERM)
    for _ in range(100):
        if process_details(pid) != details:
            PID_FILE.unlink(missing_ok=True)
            print(f"Stopped development UI (PID {pid}).")
            return
        time.sleep(0.1)
    raise SystemExit(f"Process {pid} did not exit; inspect it before stopping it manually.")


def status() -> None:
    current = managed_process()
    if current is None:
        print("Development UI is not running.")
        raise SystemExit(1)
    if not responsive():
        raise SystemExit(f"Development UI PID {current[0]} is not responding at {URL}.")
    print(f"Development UI running at {URL} (PID {current[0]}).")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", nargs="?", choices=("up", "down", "status"))
    parser.add_argument("--serve", action="store_true")
    args = parser.parse_args()
    if args.serve:
        from gmail_cleanup.ui.server import serve

        serve(open_browser=False)
    elif args.action == "up":
        start()
    elif args.action == "down":
        stop()
    elif args.action == "status":
        status()
    else:
        parser.error("Choose up, down, or status.")


if __name__ == "__main__":
    main()
