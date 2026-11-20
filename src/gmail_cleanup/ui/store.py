"""SQLite persistence scoped by authenticated issuer and subject."""

from __future__ import annotations

import json
import os
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken

from gmail_cleanup.gmail.service import ConfigurationError
from gmail_cleanup.ui.auth import Identity


class Store:
    def __init__(self, path: Path, encryption_key: str) -> None:
        try:
            self.cipher = Fernet(encryption_key.encode("ascii"))
        except (ValueError, UnicodeEncodeError) as exc:
            raise ConfigurationError("GMAIL_ENCRYPTION_KEY must be a Fernet key.") from exc
        path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.path = path
        with self.open() as db:
            db.executescript(
                """
                CREATE TABLE IF NOT EXISTS accounts (
                    issuer TEXT NOT NULL, subject TEXT NOT NULL, email TEXT NOT NULL,
                    credentials BLOB NOT NULL, PRIMARY KEY (issuer, subject, email)
                );
                CREATE TABLE IF NOT EXISTS settings (
                    issuer TEXT NOT NULL, subject TEXT NOT NULL, key TEXT NOT NULL,
                    value TEXT NOT NULL, PRIMARY KEY (issuer, subject, key)
                );
                """
            )
        os.chmod(path, 0o600)

    @contextmanager
    def open(self) -> Iterator[sqlite3.Connection]:
        db = sqlite3.connect(self.path, timeout=10)
        try:
            with db:
                yield db
        finally:
            db.close()

    def list_accounts(self, user: Identity) -> list[str]:
        with self.open() as db:
            rows = db.execute(
                "SELECT email FROM accounts WHERE issuer=? AND subject=? ORDER BY email",
                (user.issuer, user.subject),
            )
            return [row[0] for row in rows]

    def save_account(self, user: Identity, email: str, credentials: str) -> None:
        encrypted = self.cipher.encrypt(credentials.encode())
        with self.open() as db:
            db.execute(
                "INSERT OR REPLACE INTO accounts VALUES (?, ?, ?, ?)",
                (user.issuer, user.subject, email, encrypted),
            )

    def credentials(self, user: Identity, email: str) -> str:
        with self.open() as db:
            row = db.execute(
                "SELECT credentials FROM accounts WHERE issuer=? AND subject=? AND email=?",
                (user.issuer, user.subject, email),
            ).fetchone()
        if row is None:
            raise ConfigurationError("Google account is not connected to this user.")
        try:
            return self.cipher.decrypt(row[0]).decode()
        except (InvalidToken, UnicodeDecodeError) as exc:
            raise ConfigurationError("Cannot decrypt account credentials; check the key.") from exc

    def delete_account(self, user: Identity, email: str) -> None:
        with self.open() as db:
            db.execute(
                "DELETE FROM accounts WHERE issuer=? AND subject=? AND email=?",
                (user.issuer, user.subject, email),
            )
            db.execute(
                "DELETE FROM settings WHERE issuer=? AND subject=? AND key=?",
                (user.issuer, user.subject, f"account:{email}"),
            )

    def get(self, user: Identity, key: str, default: object) -> object:
        with self.open() as db:
            row = db.execute(
                "SELECT value FROM settings WHERE issuer=? AND subject=? AND key=?",
                (user.issuer, user.subject, key),
            ).fetchone()
        return json.loads(row[0]) if row else default

    def put(self, user: Identity, key: str, value: object) -> None:
        with self.open() as db:
            db.execute(
                "INSERT OR REPLACE INTO settings VALUES (?, ?, ?, ?)",
                (user.issuer, user.subject, key, json.dumps(value)),
            )
