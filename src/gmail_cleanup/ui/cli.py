"""The `ui` subcommand — launch the loopback web UI."""

from __future__ import annotations

import click


@click.command()
@click.option("--port", default=8100, show_default=True, help="Loopback port.")
@click.option("--no-browser", is_flag=True, help="Don't open a browser on start.")
def ui(port: int, no_browser: bool) -> None:
    """Build-if-needed and serve the local web UI (127.0.0.1; Ctrl-C to stop)."""
    from .server import serve

    serve(port=port, open_browser=not no_browser)
