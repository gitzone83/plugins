#!/usr/local/bin/python3
"""Dump port status for a specific switch from SQLite as JSON."""

import json
import re
import sys
import time
from lib.db import get_connection, dict_from_row
from lib.vendor import get_vendor_handler_by_key


def _format_speed(mbps):
    """Format speed in Mbps to human-readable string."""
    if not mbps or mbps == 0:
        return '-'
    if mbps >= 1000 and mbps % 1000 == 0:
        return '%dG' % (mbps // 1000)
    if mbps == 2500:
        return '2.5G'
    if mbps >= 1000:
        return '%.1fG' % (mbps / 1000.0)
    return '%dM' % mbps


def _natural_sort_key(name):
    """Return a sort key that orders interface names naturally.

    Splits name into text and numeric parts so ae2 < ae10.
    Example: 'xe-0/0/12' -> ['xe-', 0, '/', 0, '/', 12]
    """
    parts = re.split(r'(\d+)', name)
    return [int(p) if p.isdigit() else p for p in parts]


def dump_ports(switch_id):
    """Output JSON list of ports for the given switch ID."""
    conn = get_connection()

    # Look up vendor for this switch
    sw_row = conn.execute(
        "SELECT vendor FROM switches WHERE id = ?", (switch_id,)
    ).fetchone()
    vendor_key = sw_row['vendor'] if sw_row and sw_row['vendor'] else None
    vendor = get_vendor_handler_by_key(vendor_key)

    rows = conn.execute(
        "SELECT * FROM ports WHERE switch_id = ? ORDER BY port_index",
        (switch_id,)
    ).fetchall()
    conn.close()

    ports = []
    for row in rows:
        port = dict_from_row(row)
        if not vendor.is_visible_port(port.get('port_name', ''), port.get('if_type')):
            continue
        # Abbreviate port name
        port['port_name'] = vendor.short_port_name(port.get('port_name', ''))
        # Format speed
        port['speed_mbps'] = _format_speed(port.get('speed_mbps', 0))
        if port.get('last_updated'):
            port['last_updated'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(port['last_updated']))
        # Show "trunk" for ports without an access VLAN assignment
        vlan_id = port.get('vlan_id')
        if vlan_id is None or vlan_id == 0:
            port['vlan_display'] = 'trunk'
        else:
            port['vlan_display'] = str(vlan_id)
        ports.append(port)

    ports.sort(key=lambda p: _natural_sort_key(p.get('port_name', '')))

    print(json.dumps({'rows': ports}))


if __name__ == '__main__':
    switch_id = sys.argv[1] if len(sys.argv) > 1 else '0'
    try:
        switch_id = int(switch_id)
    except ValueError:
        switch_id = 0
    dump_ports(switch_id)
