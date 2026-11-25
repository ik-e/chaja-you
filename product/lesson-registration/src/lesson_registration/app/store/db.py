"""SQLite connection and transaction helpers.

Every call opens its own connection so concurrent threads/processes are
serialised by SQLite itself (``BEGIN IMMEDIATE`` takes the write lock up front).
"""

from __future__ import annotations

import contextlib
import pathlib
import secrets
import sqlite3
from collections.abc import Iterator

SCHEMA = (pathlib.Path(__file__).with_name("schema.sql")).read_text(encoding="utf-8")


class Store:
    def __init__(self, path: str | pathlib.Path) -> None:
        self.path = str(path)
        with self.connect() as conn:
            conn.executescript(SCHEMA)
            with tx(conn):
                row = conn.execute("SELECT value FROM meta WHERE key='cursor_secret'").fetchone()
                if row is None:
                    conn.execute(
                        "INSERT INTO meta(key, value) VALUES ('cursor_secret', ?)",
                        (secrets.token_hex(32),),
                    )

    @contextlib.contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.path, isolation_level=None, timeout=30)
        conn.row_factory = sqlite3.Row
        try:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA foreign_keys=ON")
            conn.execute("PRAGMA busy_timeout=30000")
            yield conn
        finally:
            conn.close()

    def cursor_secret(self) -> bytes:
        with self.connect() as conn:
            row = conn.execute("SELECT value FROM meta WHERE key='cursor_secret'").fetchone()
        return bytes.fromhex(row["value"])


@contextlib.contextmanager
def tx(conn: sqlite3.Connection) -> Iterator[sqlite3.Connection]:
    conn.execute("BEGIN IMMEDIATE")
    try:
        yield conn
    except BaseException:
        conn.execute("ROLLBACK")
        raise
    else:
        conn.execute("COMMIT")


def next_seq(conn: sqlite3.Connection, table: str) -> int:
    """Monotonic insertion order (tie-breaker for identical timestamps)."""
    if table not in {"sources", "registrations"}:
        raise ValueError(table)
    row = conn.execute(f"SELECT COALESCE(MAX(seq), 0) + 1 AS n FROM {table}").fetchone()
    return int(row["n"])
