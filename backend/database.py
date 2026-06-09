"""
Database layer using SQLite
"""
import sqlite3
import json
import os
from datetime import datetime
from typing import Optional, List, Dict

DB_PATH = os.path.join(os.path.dirname(__file__), "app.db")


class Database:
    def __init__(self):
        self._init_db()

    def _conn(self):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._conn() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    password TEXT NOT NULL,
                    display_name TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS chat_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    sender TEXT,
                    message TEXT,
                    timestamp TEXT,
                    date TEXT,
                    time TEXT,
                    hour INTEGER,
                    day_of_week TEXT,
                    message_type TEXT,
                    FOREIGN KEY(username) REFERENCES users(username)
                );

                CREATE TABLE IF NOT EXISTS chat_analysis (
                    username TEXT PRIMARY KEY,
                    analysis_json TEXT NOT NULL,
                    is_dirty INTEGER DEFAULT 0,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY(username) REFERENCES users(username)
                );

                CREATE TABLE IF NOT EXISTS user_patterns (
                    username TEXT PRIMARY KEY,
                    pattern_json TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY(username) REFERENCES users(username)
                );

                CREATE TABLE IF NOT EXISTS reply_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    incoming_message TEXT,
                    replies_json TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(username) REFERENCES users(username)
                );
            """)

    # ── Users ──────────────────────────────────────────────────────────────────

    def create_user(self, username: str, password: str, display_name: str):
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO users (username, password, display_name, created_at) VALUES (?, ?, ?, ?)",
                (username, password, display_name, datetime.now().isoformat())
            )

    def get_user(self, username: str) -> Optional[Dict]:
        with self._conn() as conn:
            row = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
            return dict(row) if row else None

    # ── Messages ───────────────────────────────────────────────────────────────

    def save_chat_messages(self, username: str, messages: List[Dict]):
        with self._conn() as conn:
            conn.execute("DELETE FROM chat_messages WHERE username = ?", (username,))
            conn.executemany(
                """INSERT INTO chat_messages
                   (username, sender, message, timestamp, date, time, hour, day_of_week, message_type)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                [
                    (
                        username,
                        m.get("sender", ""),
                        m.get("message", ""),
                        m.get("timestamp", ""),
                        m.get("date", ""),
                        m.get("time", ""),
                        m.get("hour", 0),
                        m.get("day_of_week", ""),
                        m.get("message_type", "text"),
                    )
                    for m in messages
                ]
            )

    def get_chat_messages(self, username: str) -> List[Dict]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM chat_messages WHERE username = ? ORDER BY id",
                (username,)
            ).fetchall()
            return [dict(r) for r in rows]

    # ── Analysis ───────────────────────────────────────────────────────────────

    def save_analysis(self, username: str, analysis: Dict):
        with self._conn() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO chat_analysis (username, analysis_json, is_dirty, updated_at)
                   VALUES (?, ?, 0, ?)""",
                (username, json.dumps(analysis), datetime.now().isoformat())
            )
            # Also save user pattern separately for quick access
            if "user_pattern" in analysis:
                conn.execute(
                    """INSERT OR REPLACE INTO user_patterns (username, pattern_json, updated_at)
                       VALUES (?, ?, ?)""",
                    (username, json.dumps(analysis["user_pattern"]), datetime.now().isoformat())
                )

    def get_analysis(self, username: str) -> Optional[Dict]:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM chat_analysis WHERE username = ? AND is_dirty = 0",
                (username,)
            ).fetchone()
            if row:
                return json.loads(row["analysis_json"])
            return None

    def mark_analysis_dirty(self, username: str):
        with self._conn() as conn:
            conn.execute(
                "UPDATE chat_analysis SET is_dirty = 1 WHERE username = ?",
                (username,)
            )

    def get_user_pattern(self, username: str) -> Optional[Dict]:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT pattern_json FROM user_patterns WHERE username = ?",
                (username,)
            ).fetchone()
            if row:
                return json.loads(row["pattern_json"])
            return None

    # ── Reply History ─────────────────────────────────────────────────────────

    def save_reply_history(self, username: str, incoming: str, replies: List[str]):
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO reply_history (username, incoming_message, replies_json, created_at) VALUES (?, ?, ?, ?)",
                (username, incoming, json.dumps(replies), datetime.now().isoformat())
            )

    def get_reply_history(self, username: str, limit: int = 20) -> List[Dict]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM reply_history WHERE username = ? ORDER BY id DESC LIMIT ?",
                (username, limit)
            ).fetchall()
            result = []
            for r in rows:
                d = dict(r)
                d["replies"] = json.loads(d["replies_json"])
                result.append(d)
            return result


db = Database()
