#!/usr/local/bin/python3
"""Dump switch inventory from SQLite as JSON for the API."""

import json
import time
from lib.db import get_connection, dict_from_row


def dump_switches():
    """Output JSON list of all switches."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM switches ORDER BY hostname, chassis_id"
    ).fetchall()
    conn.close()

    switches = []
    for row in rows:
        sw = dict_from_row(row)
        # Convert epoch timestamps to human-readable
        if sw.get('first_seen'):
            sw['first_seen'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(sw['first_seen']))
        if sw.get('last_seen'):
            sw['last_seen'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(sw['last_seen']))
        switches.append(sw)

    print(json.dumps({'rows': switches}))


if __name__ == '__main__':
    dump_switches()
