"""Chhota SQLite helper (yaaddasht, social connections, aur agent tasks ke liye)."""
import sqlite3
from contextlib import closing
from typing import Any, Dict, List

from . import config


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(str(config.DB_PATH), timeout=15)
    conn.row_factory = sqlite3.Row
    return conn


def execute(sql: str, params: tuple = ()) -> int:
    with closing(_connect()) as c:
        cur = c.execute(sql, params)
        c.commit()
        return cur.lastrowid or 0


def fetchall(sql: str, params: tuple = ()) -> List[Dict[str, Any]]:
    with closing(_connect()) as c:
        return [dict(r) for r in c.execute(sql, params).fetchall()]


def fetchone(sql: str, params: tuple = ()) -> Dict[str, Any] | None:
    rows = fetchall(sql, params)
    return rows[0] if rows else None


def init() -> None:
    execute(
        "CREATE TABLE IF NOT EXISTS memories("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, text TEXT NOT NULL, created REAL NOT NULL)"
    )
    execute("CREATE TABLE IF NOT EXISTS tasks(id TEXT PRIMARY KEY, data TEXT NOT NULL, updated REAL NOT NULL)")
    execute(
        "CREATE TABLE IF NOT EXISTS connections("
        "platform TEXT PRIMARY KEY, data TEXT NOT NULL, updated REAL NOT NULL)"
    )


init()
