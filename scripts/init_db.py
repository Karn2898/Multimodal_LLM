
from __future__ import annotations

import os
import sqlite3
from pathlib import Path

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///chat_history.db")
DB_PATH = Path("chat_history.db")

CREATE_SESSIONS_TABLE = """
CREATE TABLE IF NOT EXISTS chat_sessions (
    id          TEXT PRIMARY KEY,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_MESSAGES_TABLE = """
CREATE TABLE IF NOT EXISTS chat_messages (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id  TEXT NOT NULL REFERENCES chat_sessions(id),
    role        TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
    content     TEXT NOT NULL,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""


def init_db() -> None:
    """Initialise the SQLite database with required tables."""
    print(f"Initialising database at '{DB_PATH}' …")
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(CREATE_SESSIONS_TABLE)
        conn.execute(CREATE_MESSAGES_TABLE)
        conn.commit()
    print("Database initialised successfully.")


if __name__ == "__main__":
    init_db()
