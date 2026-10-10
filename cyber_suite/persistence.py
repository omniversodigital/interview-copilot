# Persistence and Logging Utilities

"""persistence.py
Provides simple encrypted SQLite storage for scan results, exploit sessions,
and audit logs. Uses `pysqlcipher3` which wraps SQLCipher for encryption.
"""

import os
import json
import datetime
from typing import Any, Dict, List

# Try to use encrypted SQLite via pysqlcipher3; fall back to plain sqlite3 if unavailable
try:
    import pysqlcipher3 as sqlite3  # type: ignore
    _ENCRYPTION_ENABLED = True
except Exception:
    import sqlite3
    _ENCRYPTION_ENABLED = False

# Path for the database file (inside the project folder)
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "cyber_data.db"))

# Encryption key – in a real deployment this should be generated securely and
# stored outside the codebase. For demonstration we derive it from a fixed
# passphrase.
_ENCRYPTION_KEY = "SovereignCyberKey2026"

def _get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    # Enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON;")
    # Apply encryption key only if encryption is enabled
    if _ENCRYPTION_ENABLED:
        conn.execute(f"PRAGMA key = '{_ENCRYPTION_KEY}';")
    return conn

def initialize_db():
    """Create tables if they do not exist.
    Tables:
      scans(id INTEGER PK, target TEXT, tool TEXT, result TEXT, ts DATETIME)
      sessions(id INTEGER PK, session_id TEXT, tool TEXT, info TEXT, ts DATETIME)
      logs(id INTEGER PK, level TEXT, message TEXT, ts DATETIME)
    """
    conn = _get_connection()
    cur = conn.cursor()
    cur.executescript(
        """
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target TEXT NOT NULL,
            tool TEXT NOT NULL,
            result TEXT NOT NULL,
            ts DATETIME NOT NULL
        );
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            tool TEXT NOT NULL,
            info TEXT NOT NULL,
            ts DATETIME NOT NULL
        );
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            level TEXT NOT NULL,
            message TEXT NOT NULL,
            ts DATETIME NOT NULL
        );
        """
    )
    conn.commit()
    conn.close()

def log_event(level: str, message: str):
    conn = _get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO logs (level, message, ts) VALUES (?, ?, ?)",
        (level.upper(), message, datetime.datetime.utcnow())
    )
    conn.commit()
    conn.close()

def save_scan(target: str, tool: str, result: Any):
    conn = _get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO scans (target, tool, result, ts) VALUES (?, ?, ?, ?)",
        (target, tool, json.dumps(result), datetime.datetime.utcnow())
    )
    conn.commit()
    conn.close()

def load_scans(limit: int = 100) -> List[Dict[str, Any]]:
    conn = _get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT target, tool, result, ts FROM scans ORDER BY ts DESC LIMIT ?", (limit,)
    )
    rows = cur.fetchall()
    conn.close()
    return [
        {
            "target": r[0],
            "tool": r[1],
            "result": json.loads(r[2]),
            "timestamp": r[3],
        }
        for r in rows
    ]

def save_session(session_id: str, tool: str, info: Any):
    conn = _get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO sessions (session_id, tool, info, ts) VALUES (?, ?, ?, ?)",
        (session_id, tool, json.dumps(info), datetime.datetime.utcnow())
    )
    conn.commit()
    conn.close()

def load_sessions() -> List[Dict[str, Any]]:
    conn = _get_connection()
    cur = conn.cursor()
    cur.execute("SELECT session_id, tool, info, ts FROM sessions ORDER BY ts DESC")
    rows = cur.fetchall()
    conn.close()
    return [
        {
            "session_id": r[0],
            "tool": r[1],
            "info": json.loads(r[2]),
            "timestamp": r[3],
        }
        for r in rows
    ]

# Ensure DB is ready on import
initialize_db()
