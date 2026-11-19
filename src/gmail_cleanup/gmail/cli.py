"""The gmail command entry point.

A bare invocation shows help; `--version` prints the version. Subcommands live in
their own sub-packages (gmail_cleanup.<tool>.cli); keep cross-cutting logic in
``gmail_cleanup.common``.
"""

from __future__ import annotations

import click

from gmail_cleanup.ui.cli import ui as _ui_cmd
from gmail_cleanup.version import __version__


@click.group(invoke_without_command=True)
@click.version_option(__version__, prog_name="gmail")
@click.pass_context
def main(ctx: click.Context) -> None:
    """a utility to clear out old gmail items"""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


def _register_subcommands() -> None:
    """Attach the tool subcommands to the umbrella group."""
    main.add_command(_ui_cmd, name="ui")


_register_subcommands()


if __name__ == "__main__":
    main()
