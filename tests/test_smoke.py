"""Smoke test: the package imports and exposes a version."""

from __future__ import annotations

from gmail_cleanup import __version__


def test_version_is_a_string():
    assert isinstance(__version__, str)
    assert __version__
