from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from app.config import get_settings
from app.schemas import MemoryRecord


def _sqlite_path(database_url: str) -> str:
    if database_url.startswith("sqlite:///"):
        return database_url.replace("sqlite:///", "", 1)
    # This keeps the interface Postgres-ready without pretending this local
    # memory implementation is a full SQLAlchemy adapter.
    raise ValueError("Local memory supports sqlite:/// URLs. Use a production adapter for Postgres.")


class MemoryStore:
    def __init__(self, database_url: str | None = None) -> None:
        self.database_url = database_url or get_settings().database_url
        self.path = _sqlite_path(self.database_url)
        self._memory_connection: sqlite3.Connection | None = None
        if self.path != ":memory:":
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self.init()

    @contextmanager
    def connect(self):
        if self.path == ":memory:":
            if self._memory_connection is None:
                self._memory_connection = sqlite3.connect(self.path)
                self._memory_connection.row_factory = sqlite3.Row
            connection = self._memory_connection
            yield connection
            connection.commit()
            return
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
            connection.commit()
        finally:
            connection.close()

    def init(self) -> None:
        with self.connect() as db:
            db.execute(
                """
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT NOT NULL,
                    value TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            db.execute("CREATE INDEX IF NOT EXISTS idx_memories_key ON memories(key)")
            db.execute("CREATE INDEX IF NOT EXISTS idx_memories_value ON memories(value)")

    def save(self, key: str, value: str) -> MemoryRecord:
        now = datetime.now(timezone.utc).isoformat()
        with self.connect() as db:
            cursor = db.execute(
                "INSERT INTO memories (key, value, created_at, updated_at) VALUES (?, ?, ?, ?)",
                (key, value, now, now),
            )
            row = db.execute("SELECT * FROM memories WHERE id = ?", (cursor.lastrowid,)).fetchone()
            return self._record(row)

    def list(self) -> list[MemoryRecord]:
        with self.connect() as db:
            rows = db.execute("SELECT * FROM memories ORDER BY updated_at DESC").fetchall()
            return [self._record(row) for row in rows]

    def delete(self, memory_id: int) -> bool:
        with self.connect() as db:
            cursor = db.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
            return cursor.rowcount > 0

    def retrieve(self, query: str, limit: int = 5) -> list[MemoryRecord]:
        pattern = f"%{query}%"
        with self.connect() as db:
            rows = db.execute(
                """
                SELECT * FROM memories
                WHERE key LIKE ? OR value LIKE ?
                ORDER BY updated_at DESC
                LIMIT ?
                """,
                (pattern, pattern, limit),
            ).fetchall()
            return [self._record(row) for row in rows]

    @staticmethod
    def _record(row: sqlite3.Row) -> MemoryRecord:
        return MemoryRecord(
            id=row["id"],
            key=row["key"],
            value=row["value"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )
