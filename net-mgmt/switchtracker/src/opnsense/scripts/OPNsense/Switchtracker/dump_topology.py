#!/usr/local/bin/python3
"""Dump network topology (nodes + edges) from SQLite as JSON for D3.js."""

import json
from lib.db import get_connection, dict_from_row


def dump_topology():
    """Output JSON with nodes and edges arrays."""
    conn = get_connection()

    # Nodes = all switches
    switch_rows = conn.execute(
        "SELECT id, chassis_id, hostname, mgmt_ip, is_online FROM switches ORDER BY hostname"
    ).fetchall()

    nodes = []
    for row in switch_rows:
        sw = dict_from_row(row)
        nodes.append({
            'id': sw['id'],
            'label': sw['hostname'] or sw['chassis_id'],
            'ip': sw.get('mgmt_ip', ''),
            'online': sw.get('is_online', 0) == 1,
        })

    # Add node 0 for this OPNsense device
    nodes.insert(0, {
        'id': 0,
        'label': 'OPNsense',
        'ip': '',
        'online': True,
    })

    # Edges = all links
    link_rows = conn.execute(
        "SELECT local_switch_id, local_port, remote_switch_id, remote_port FROM links"
    ).fetchall()
    conn.close()

    edges = []
    for row in link_rows:
        link = dict_from_row(row)
        edges.append({
            'source': link['local_switch_id'],
            'target': link.get('remote_switch_id') or 0,
            'sourcePort': link.get('local_port', ''),
            'targetPort': link.get('remote_port', ''),
        })

    print(json.dumps({'nodes': nodes, 'edges': edges}))


if __name__ == '__main__':
    dump_topology()
