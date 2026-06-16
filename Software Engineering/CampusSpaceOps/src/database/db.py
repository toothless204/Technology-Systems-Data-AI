import sqlite3
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DB_PATH, SCHEMA, SEED_FILE


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def initialize_db(seed: bool = True) -> None:
    conn = get_connection()
    with open(SCHEMA, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    if seed and os.path.exists(SEED_FILE):
        # Only seed if no users exist yet
        cur = conn.execute("SELECT COUNT(*) FROM users")
        if cur.fetchone()[0] == 0:
            with open(SEED_FILE, "r", encoding="utf-8") as f:
                conn.executescript(f.read())
    conn.commit()
    conn.close()


# ---------- generic helpers ----------

def fetchall(sql: str, params: tuple = ()) -> list[sqlite3.Row]:
    conn = get_connection()
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return rows


def fetchone(sql: str, params: tuple = ()) -> sqlite3.Row | None:
    conn = get_connection()
    row = conn.execute(sql, params).fetchone()
    conn.close()
    return row


def execute(sql: str, params: tuple = ()) -> int:
    """Execute INSERT/UPDATE/DELETE and return lastrowid or rowcount."""
    conn = get_connection()
    cur = conn.execute(sql, params)
    conn.commit()
    result = cur.lastrowid
    conn.close()
    return result
