import sqlite3
import os
from contextlib import contextmanager
from app.core.config import settings

DB_FILE = "alas.db"


def get_db_path() -> str:
    """Returns absolute path to SQLite database."""
    if settings.DATABASE_URL.startswith("sqlite:///"):
        path_str = settings.DATABASE_URL.replace("sqlite:///", "")
        return os.path.abspath(path_str)
    return os.path.abspath(DB_FILE)


@contextmanager
def get_db_connection():
    """Provides a transactional database connection context."""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path, timeout=10.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
