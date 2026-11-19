"""Single source of the package version."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("gmail-cleanup")
except PackageNotFoundError:  # running from a source tree, not installed
    __version__ = "0.1.0"
