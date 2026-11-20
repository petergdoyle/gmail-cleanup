"""Verify cleanup behavior without contacting Gmail or accessing a real Keychain."""

import os
from datetime import date
from unittest.mock import Mock

import pytest
from click.testing import CliRunner
from googleapiclient.errors import HttpError
from httplib2 import Response
from oauthlib.oauth2 import AccessDeniedError

from gmail_cleanup.gmail import service
from gmail_cleanup.gmail.cli import main


@pytest.mark.parametrize(
    ("text", "months"), [("3mo", 3), ("6MO", 6), (" 12mo ", 12)]
)
def test_parse_age(text, months):
    assert service.parse_age(text) == months


@pytest.mark.parametrize("text", ["0mo", "-3mo", "3m", "3.5mo", "", "1mo extra"])
def test_reject_invalid_age(text):
    with pytest.raises(ValueError):
        service.parse_age(text)


def test_queries_are_scoped_and_date_is_formatted_for_gmail():
    assert service.Mailbox("inbox", months=6).query() == "in:inbox older_than:6m"
    assert service.Mailbox("archive", before=date(2026, 3, 5)).query() == (
        "-in:inbox -in:sent -in:drafts -in:spam -in:trash before:2026/03/05"
    )
    with pytest.raises(ValueError):
        service.Mailbox("archive", months=3, before=date(2026, 3, 5)).query()


def test_preview_collects_all_pages_and_deduplicates():
    messages = Mock()
    messages.list.return_value.execute.side_effect = [
        {"messages": [{"id": "a"}, {"id": "b"}], "nextPageToken": "next"},
        {"messages": [{"id": "b"}, {"id": "c"}]},
    ]
    client = Mock()
    client.users.return_value.messages.return_value = messages
    result = service.preview(client, "one@example.com", [service.Mailbox("inbox", months=6)])
    assert result.matches == {"inbox": ("a", "b", "c")}
    assert result.total == 3
    assert messages.list.call_args_list[1].kwargs["pageToken"] == "next"
    messages.trash.assert_not_called()


def test_wrong_account_is_rejected(monkeypatch):
    monkeypatch.setattr(service, "credentials_for", lambda *args, **kwargs: Mock())
    monkeypatch.setattr(service, "gmail_client", lambda credentials: Mock())
    monkeypatch.setattr(service, "profile", lambda client: "other@example.com")
    with pytest.raises(service.ConfigurationError, match="not requested account"):
        service.connect("one@example.com")


def test_authorized_account_is_stored_in_keychain(monkeypatch):
    store = Mock()
    store.get_password.return_value = None
    credentials = Mock(refresh_token="test-refresh-token")
    credentials.to_json.return_value = '{"refresh_token":"test-refresh-token"}'
    flow = Mock()
    flow.run_local_server.return_value = credentials
    monkeypatch.setattr(service, "_keyring", lambda: store)
    monkeypatch.setattr(service, "client_config", lambda *args: {"installed": {}})
    monkeypatch.setattr(service.InstalledAppFlow, "from_client_config", lambda *args: flow)
    monkeypatch.setattr(service, "gmail_client", lambda credentials: Mock())
    monkeypatch.setattr(service, "profile", lambda client: "one@example.com")
    assert service.add_account() == "one@example.com"
    assert store.set_password.call_count == 2
    assert store.set_password.call_args_list[0].args[1] == "one@example.com"
    assert store.set_password.call_args_list[1].args[1] == service.ACCOUNT_INDEX
    assert flow.run_local_server.call_args.kwargs["timeout_seconds"] == 180


def test_export_credentials_is_private_and_never_uses_symlink(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    store = Mock()
    store.get_password.return_value = '{"refresh_token":"fake"}'
    monkeypatch.setattr(service, "_keyring", lambda: store)
    path = service.export_credentials("one@example.com")
    assert path.stat().st_mode & 0o777 == 0o600
    assert "GMAIL_AUTHORIZED_USER_JSON" in path.read_text()
    path.unlink()
    target = tmp_path / "other"
    target.write_text("unchanged")
    os.symlink(target, path)
    with pytest.raises(service.ConfigurationError, match="symlink"):
        service.export_credentials("one@example.com")
    assert target.read_text() == "unchanged"


def test_injected_credentials_precede_env_file(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env").write_text("EXAMPLE_SETTING=from-file\n")
    monkeypatch.setenv("EXAMPLE_SETTING", "from-environment")
    assert service.setting("EXAMPLE_SETTING") == "from-environment"


def test_cleanup_stops_on_error_and_reports_partial_count():
    messages = Mock()
    messages.trash.return_value.execute.side_effect = [
        {},
        HttpError(Response({"status": "403"}), b"forbidden"),
    ]
    client = Mock()
    client.users.return_value.messages.return_value = messages
    result = service.Preview("one@example.com", {"inbox": ("a", "b", "c")}, {})
    with pytest.raises(service.CleanupError, match="after moving 1"):
        service.move_to_trash(client, result)
    assert [call.kwargs["id"] for call in messages.trash.call_args_list] == ["a", "b"]


def test_cli_dry_run_never_moves_and_uses_defaults(monkeypatch):
    client = Mock()
    received = []
    monkeypatch.setattr(service, "connect", lambda account: client)

    def fake_preview(client_arg, account, boxes):
        received.extend(boxes)
        return service.Preview(account, {"inbox": ("a",), "archive": ("b",)}, {})

    # CLI displays the query for each selected mailbox.
    def preview_with_queries(client_arg, account, boxes):
        result = fake_preview(client_arg, account, boxes)
        return service.Preview(account, result.matches, {box.name: box.query() for box in boxes})

    move = Mock()
    monkeypatch.setattr(service, "preview", preview_with_queries)
    monkeypatch.setattr(service, "move_to_trash", move)
    result = CliRunner().invoke(main, ["delete", "--account", "one@example.com", "--dry-run"])
    assert result.exit_code == 0, result.output
    assert [box.query() for box in received] == [
        "in:inbox older_than:6m",
        "-in:inbox -in:sent -in:drafts -in:spam -in:trash older_than:3m",
    ]
    assert "Total: 2 messages" in result.output
    assert "Moving a message to Trash affects all its labels." in result.output
    assert "Archive includes eligible messages with custom labels." in result.output
    move.assert_not_called()


def test_cli_confirmation_and_explicit_yes(monkeypatch):
    client = Mock()
    result = service.Preview(
        "one@example.com", {"inbox": ("a",)}, {"inbox": "in:inbox older_than:6m"}
    )
    monkeypatch.setattr(service, "connect", lambda account: client)
    monkeypatch.setattr(service, "preview", lambda *args: result)
    move = Mock(return_value=1)
    monkeypatch.setattr(service, "move_to_trash", move)
    runner = CliRunner()
    declined = runner.invoke(main, ["delete", "--account", "one@example.com"], input="n\n")
    assert declined.exit_code != 0
    move.assert_not_called()
    accepted = runner.invoke(main, ["delete", "--account", "one@example.com", "--yes"])
    assert accepted.exit_code == 0, accepted.output
    move.assert_called_once_with(client, result)


def test_oauth_denial_is_reported_without_traceback(monkeypatch):
    def deny(*args, **kwargs):
        raise AccessDeniedError()

    monkeypatch.setattr(service, "add_account", deny)
    result = CliRunner().invoke(main, ["auth"])
    assert result.exit_code != 0
    assert "Google authorization failed" in result.output
