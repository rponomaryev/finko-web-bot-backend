import os
import sqlite3
from contextlib import closing

from app.config import settings


def ensure_db_directory() -> None:
    db_path = settings.DATABASE_PATH
    db_dir = os.path.dirname(db_path)

    if db_dir:
        os.makedirs(db_dir, exist_ok=True)


def get_connection() -> sqlite3.Connection:
    ensure_db_directory()
    conn = sqlite3.connect(settings.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with closing(get_connection()) as conn:
        with conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS chat_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    page TEXT,
                    language TEXT NOT NULL,
                    user_message TEXT NOT NULL,
                    assistant_answer TEXT NOT NULL,
                    sources_used INTEGER NOT NULL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS feedback_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    rating INTEGER NOT NULL,
                    comment TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)


def log_chat(
    session_id: str,
    page: str | None,
    language: str,
    user_message: str,
    assistant_answer: str,
    sources_used: bool,
) -> None:
    with closing(get_connection()) as conn:
        with conn:
            conn.execute("""
                INSERT INTO chat_logs (
                    session_id,
                    page,
                    language,
                    user_message,
                    assistant_answer,
                    sources_used
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                session_id,
                page,
                language,
                user_message,
                assistant_answer,
                int(sources_used),
            ))


def log_feedback(session_id: str, rating: int, comment: str | None) -> None:
    with closing(get_connection()) as conn:
        with conn:
            conn.execute("""
                INSERT INTO feedback_logs (
                    session_id,
                    rating,
                    comment
                ) VALUES (?, ?, ?)
            """, (
                session_id,
                rating,
                comment,
            ))