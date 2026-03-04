#!/usr/local/bin/python3
"""Dump port status for a specific switch from SQLite as JSON."""

import json
import sys
import time
from lib.db import get_connection, dict_from_row


def dump_ports(switch_id):
    """Output JSON list of ports for the given switch ID."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM ports WHERE switch_id = ? ORDER BY port_index",
        (switch_id,)
    ).fetchall()
    conn.close()

    ports = []
    for row in rows:
        port = dict_from_row(row)
        if port.get('last_updated'):
            port['last_updated'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(port['last_updated']))
        ports.append(port)

    print(json.dumps({'rows': ports}))


if __name__ == '__main__':
    switch_id = sys.argv[1] if len(sys.argv) > 1 else '0'
    try:
        switch_id = int(switch_id)
    except ValueError:
        switch_id = 0
    dump_ports(switch_id)
