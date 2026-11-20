"""Verify managed development startup opens only a ready UI."""

from unittest.mock import Mock

import pytest

from gmail_cleanup.ui import dev


def test_running_ui_opens_browser_when_responsive(monkeypatch):
    browser = Mock(return_value=True)
    monkeypatch.setattr(dev, "managed_process", lambda: (123, "managed"))
    monkeypatch.setattr(dev, "responsive", lambda: True)
    monkeypatch.setattr(dev.webbrowser, "open", browser)
    dev.start()
    browser.assert_called_once_with(dev.URL)


def test_new_ui_opens_browser_after_ready(tmp_path, monkeypatch):
    process = Mock(pid=123)
    process.poll.return_value = None
    browser = Mock(return_value=True)
    responses = iter([False, False, True])
    monkeypatch.setattr(dev, "RUN_DIR", tmp_path)
    monkeypatch.setattr(dev, "PID_FILE", tmp_path / "pid.json")
    monkeypatch.setattr(dev, "managed_process", lambda: None)
    monkeypatch.setattr(dev, "responsive", lambda: next(responses))
    monkeypatch.setattr(dev, "process_details", lambda pid: "managed")
    monkeypatch.setattr(dev.subprocess, "Popen", lambda *args, **kwargs: process)
    monkeypatch.setattr(dev.time, "sleep", lambda delay: None)
    monkeypatch.setattr(dev.webbrowser, "open", browser)
    dev.start()
    browser.assert_called_once_with(dev.URL)


def test_unready_ui_does_not_open_browser(monkeypatch):
    browser = Mock()
    monkeypatch.setattr(dev, "managed_process", lambda: (123, "managed"))
    monkeypatch.setattr(dev, "responsive", lambda: False)
    monkeypatch.setattr(dev.webbrowser, "open", browser)
    with pytest.raises(SystemExit, match="not responding"):
        dev.start()
    browser.assert_not_called()


@pytest.mark.parametrize("outcome", [False, dev.webbrowser.Error("browser unavailable")])
def test_browser_failure_prints_manual_url(monkeypatch, capsys, outcome):
    browser = Mock()
    if isinstance(outcome, Exception):
        browser.side_effect = outcome
    else:
        browser.return_value = outcome
    monkeypatch.setattr(dev.webbrowser, "open", browser)
    dev.open_browser()
    assert dev.URL in capsys.readouterr().out
