"""Database utilities with simple SQLite connection pooling and safe query helpers.

Features:
- Connection pooling for SQLite (thread-safe queue)
- Context manager for acquiring/releasing connections
- Parameterized queries to avoid SQL injection
- Helper functions: fetch_one, fetch_all, execute, executemany

Note: For PostgreSQL, extend this module to use psycopg2/asyncpg with proper DSN.
"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from queue import Queue, Empty
from threading import Lock
from typing import Any, Iterable, List, Optional, Tuple


class SQLiteConnectionPool:
    def __init__(self, db_path: Path, pool_size: int = 5) -> None:
        self.db_path = db_path
        self.pool_size = max(1, pool_size)
        self._pool: Queue[sqlite3.Connection] = Queue(maxsize=self.pool_size)
        self._lock = Lock()
        for _ in range(self.pool_size):
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            self._pool.put(conn)

    @contextmanager
    def connection(self) -> sqlite3.Connection:
        conn: Optional[sqlite3.Connection] = None
        try:
            conn = self._pool.get(timeout=5)
            yield conn
        finally:
            if conn:
                self._pool.put(conn)

    def close_all(self) -> None:
        with self._lock:
            while True:
                try:
                    conn = self._pool.get_nowait()
                except Empty:
                    break
                conn.close()


def get_sqlite_pool(db_path: str | Path, pool_size: int = 5) -> SQLiteConnectionPool:
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    return SQLiteConnectionPool(path, pool_size=pool_size)


def fetch_one(conn: sqlite3.Connection, query: str, params: Tuple[Any, ...] = ()) -> Optional[sqlite3.Row]:
    cur = conn.cursor()
    cur.execute(query, params)
    return cur.fetchone()


def fetch_all(conn: sqlite3.Connection, query: str, params: Tuple[Any, ...] = ()) -> List[sqlite3.Row]:
    cur = conn.cursor()
    cur.execute(query, params)
    return cur.fetchall()


def execute(conn: sqlite3.Connection, query: str, params: Tuple[Any, ...] = ()) -> int:
    cur = conn.cursor()
    cur.execute(query, params)
    conn.commit()
    return cur.rowcount


def executemany(conn: sqlite3.Connection, query: str, params: Iterable[Tuple[Any, ...]]) -> int:
    cur = conn.cursor()
    cur.executemany(query, params)
    conn.commit()
    return cur.rowcount
