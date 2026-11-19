"""Shared core for gmail-cleanup — cross-cutting logic the rest of the package draws from.

Per the stack's import discipline: other sub-packages may import from ``common``;
they must not import each other. (In a CLI project the umbrella command is the one
place above the tools that composes them.)
"""
