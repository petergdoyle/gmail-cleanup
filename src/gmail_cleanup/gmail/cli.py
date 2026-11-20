"""The gmail command entry point.

A bare invocation shows help; `--version` prints the version. Subcommands live in
their own sub-packages (gmail_cleanup.<tool>.cli); keep cross-cutting logic in
``gmail_cleanup.common``.
"""

from __future__ import annotations

import webbrowser
from datetime import UTC, datetime

import click
from google.auth.exceptions import GoogleAuthError
from google_auth_oauthlib.flow import WSGITimeoutError
from googleapiclient.errors import HttpError
from httplib2 import HttpLib2Error
from keyring.errors import KeyringError
from oauthlib.oauth2 import OAuth2Error

from gmail_cleanup.gmail import service
from gmail_cleanup.ui.cli import ui as _ui_cmd
from gmail_cleanup.version import __version__


@click.group(invoke_without_command=True)
@click.version_option(__version__, prog_name="gmail")
@click.pass_context
def main(ctx: click.Context) -> None:
    """a utility to clear out old gmail items"""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@click.command("auth")
@click.option("--credentials-path", type=click.Path(path_type=str), default=None)
def auth(credentials_path: str | None) -> None:
    """Authorize a Google account and save its credentials in macOS Keychain."""
    try:
        email = service.add_account(path=credentials_path)
    except service.ConfigurationError as exc:
        raise click.ClickException(str(exc)) from exc
    except (
        HttpError, HttpLib2Error, GoogleAuthError, KeyringError, OAuth2Error, OSError,
        ValueError, WSGITimeoutError, webbrowser.Error,
    ) as exc:
        raise click.ClickException("Google authorization failed; check the OAuth setup.") from exc
    click.echo(f"Authorized account: {email}")


@click.command("accounts")
def list_accounts() -> None:
    """List accounts authorized in macOS Keychain."""
    try:
        result = service.accounts()
    except service.ConfigurationError as exc:
        raise click.ClickException(str(exc)) from exc
    except KeyringError as exc:
        raise click.ClickException("Cannot access macOS Keychain.") from exc
    if not result:
        click.echo("No accounts authorized. Run gmail auth.")
    for email in result:
        click.echo(email)


@click.command("test-connection")
@click.option("--account", required=True, help="Google account email to test.")
def test_connection(account: str) -> None:
    """Test access to the selected Gmail account."""
    try:
        service.connect(account)
    except service.ConfigurationError as exc:
        raise click.ClickException(str(exc)) from exc
    except (HttpError, HttpLib2Error, GoogleAuthError, KeyringError, OSError) as exc:
        raise click.ClickException(
            "Gmail connection failed; check access and credentials."
        ) from exc
    click.echo(f"Gmail connection succeeded for {account}.")


@click.command("export-credentials")
@click.option("--account", required=True, help="Account to copy from macOS Keychain.")
def export_credentials(account: str) -> None:
    """Save one account's OAuth credentials in the current directory's .env."""
    click.confirm(
        "Store reusable credentials as plaintext in .env for scheduled CLI use? "
        "This replaces any existing injected account credential",
        abort=True,
    )
    try:
        service.export_credentials(account)
    except service.ConfigurationError as exc:
        raise click.ClickException(str(exc)) from exc
    except (KeyringError, OSError) as exc:
        raise click.ClickException("Cannot export credentials to .env.") from exc
    click.echo("Credentials saved to .env with owner-only permissions; keep it private.")


@click.command("delete")
@click.option("--account", required=True, help="Google account email to clean.")
@click.option("--inbox/--no-inbox", default=True, show_default=True)
@click.option("--archive/--no-archive", default=True, show_default=True)
@click.option("--inbox-age", default="6mo", show_default=True)
@click.option("--archive-age", default="3mo", show_default=True)
@click.option("--dry-run", is_flag=True, help="Preview only; never change mail.")
@click.option("--yes", is_flag=True, help="Confirm moving the previewed messages to Trash.")
def delete(
    account: str, inbox: bool, archive: bool, inbox_age: str, archive_age: str,
    dry_run: bool, yes: bool,
) -> None:
    """Preview and move old mail to Gmail Trash for one account."""
    try:
        boxes = []
        if inbox:
            boxes.append(service.Mailbox("inbox", months=service.parse_age(inbox_age)))
        if archive:
            boxes.append(service.Mailbox("archive", months=service.parse_age(archive_age)))
        if not boxes:
            raise ValueError("Select at least one mailbox.")
        client = service.connect(account)
        result = service.preview(client, account, boxes)
        click.echo(f"Account: {account}")
        for name, ids in result.matches.items():
            click.echo(f"{name}: {len(ids)} messages ({result.queries[name]})")
        click.echo(f"Total: {result.total} messages")
        click.echo(
            "Moving a message to Trash affects all its labels. "
            "Archive includes eligible messages with custom labels."
        )
        if dry_run:
            click.echo("Dry run: no messages moved.")
            return
        if not result.total:
            click.echo("No messages to move.")
            return
        if not yes:
            click.confirm(
                f"Move these {result.total} messages to Gmail Trash for {account}?",
                abort=True,
            )
        moved = service.move_to_trash(client, result)
        completed_at = datetime.now(UTC).isoformat()
        click.echo(f"Moved {moved} messages to Gmail Trash for {account} at {completed_at}.")
    except (service.ConfigurationError, service.CleanupError, ValueError) as exc:
        raise click.ClickException(str(exc)) from exc
    except (HttpError, HttpLib2Error, GoogleAuthError, KeyringError, OSError) as exc:
        raise click.ClickException("Gmail operation failed; check access and credentials.") from exc


def _register_subcommands() -> None:
    """Attach the tool subcommands to the umbrella group."""
    main.add_command(_ui_cmd, name="ui")
    main.add_command(auth)
    main.add_command(list_accounts)
    main.add_command(test_connection)
    main.add_command(export_credentials)
    main.add_command(delete)


_register_subcommands()


if __name__ == "__main__":
    main()
