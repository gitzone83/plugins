"""SQLite database wrapper for Switch Tracker."""

import os
import sqlite3

DB_PATH = '/var/switchtracker/switchtracker.sqlite'
SCHEMA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'sql', 'init.sql')


def get_connection():
    """Get a SQLite connection, creating the database and schema if needed."""
    db_dir = os.path.dirname(DB_PATH)
    if not os.path.isdir(db_dir):
        os.makedirs(db_dir, mode=0o750, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")

    # Initialize schema if tables don't exist
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='switches'")
    if cursor.fetchone() is None:
        with open(SCHEMA_PATH, 'r') as f:
            conn.executescript(f.read())
        conn.commit()

    return conn


def dict_from_row(row):
    """Convert a sqlite3.Row to a dict."""
    if row is None:
        return None
    return dict(row)
