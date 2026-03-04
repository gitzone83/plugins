"""SQLite database wrapper for Switch Tracker."""

import os
import socket
import sqlite3
import time

DB_PATH = '/var/switchtracker/switchtracker.sqlite'
SCHEMA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'sql', 'init.sql')

SELF_CHASSIS_ID = '__opnsense_self__'


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

    # Migrate: add columns introduced in later versions
    _ensure_columns(conn)

    # Ensure the "self" OPNsense device exists as switch id 1
    self_row = conn.execute(
        "SELECT id FROM switches WHERE chassis_id = ?", (SELF_CHASSIS_ID,)
    ).fetchone()
    if self_row is None:
        now = time.time()
        hostname = socket.gethostname()
        conn.execute(
            """INSERT INTO switches (chassis_id, hostname, source, first_seen, last_seen, is_online)
               VALUES (?, ?, 'local', ?, ?, 1)""",
            (SELF_CHASSIS_ID, hostname, now, now)
        )
        conn.commit()

    return conn


def _ensure_columns(conn):
    """Add columns introduced in later versions if they don't exist."""
    migrations = [
        ('switches', 'vendor', 'TEXT'),
        ('ports', 'if_type', 'INTEGER'),
        ('ports', 'in_pkts', 'INTEGER DEFAULT 0'),
        ('ports', 'out_pkts', 'INTEGER DEFAULT 0'),
    ]
    for table, column, col_type in migrations:
        cols = [row[1] for row in conn.execute("PRAGMA table_info(%s)" % table).fetchall()]
        if column not in cols:
            conn.execute("ALTER TABLE %s ADD COLUMN %s %s" % (table, column, col_type))
    conn.commit()


def get_self_id(conn):
    """Return the switch ID for the local OPNsense device."""
    row = conn.execute(
        "SELECT id FROM switches WHERE chassis_id = ?", (SELF_CHASSIS_ID,)
    ).fetchone()
    return row['id'] if row else None


def dict_from_row(row):
    """Convert a sqlite3.Row to a dict."""
    if row is None:
        return None
    return dict(row)
