#!/usr/local/bin/python3
"""Poll LLDP neighbors and update the SQLite switch inventory."""

import time
from lib.db import get_connection
from lib.lldp_client import get_lldp_neighbors


def poll_lldp():
    """Discover switches via LLDP and upsert into SQLite."""
    neighbors = get_lldp_neighbors()
    if not neighbors:
        return

    conn = get_connection()
    now = time.time()

    for neighbor in neighbors:
        chassis_id = neighbor['chassis_id']

        # Upsert switch
        existing = conn.execute(
            "SELECT id FROM switches WHERE chassis_id = ?", (chassis_id,)
        ).fetchone()

        if existing:
            conn.execute(
                """UPDATE switches SET hostname = ?, mgmt_ip = ?, mac_address = ?,
                   model = ?, last_seen = ?, is_online = 1
                   WHERE chassis_id = ?""",
                (neighbor['hostname'], neighbor['mgmt_ip'], neighbor['mac_address'],
                 neighbor['model'], now, chassis_id)
            )
            switch_id = existing['id']
        else:
            cursor = conn.execute(
                """INSERT INTO switches (chassis_id, hostname, mgmt_ip, mac_address,
                   model, source, first_seen, last_seen, is_online)
                   VALUES (?, ?, ?, ?, ?, 'lldp', ?, ?, 1)""",
                (chassis_id, neighbor['hostname'], neighbor['mgmt_ip'],
                 neighbor['mac_address'], neighbor['model'], now, now)
            )
            switch_id = cursor.lastrowid

        # Upsert link
        local_port = neighbor.get('local_port', '')
        remote_port = neighbor.get('remote_port', '')
        if local_port:
            # Use a synthetic local switch ID (0 = this OPNsense device)
            existing_link = conn.execute(
                """SELECT id FROM links
                   WHERE local_switch_id = 0 AND local_port = ? AND remote_chassis_id = ?""",
                (local_port, chassis_id)
            ).fetchone()

            if existing_link:
                conn.execute(
                    "UPDATE links SET remote_port = ?, remote_switch_id = ?, last_seen = ? WHERE id = ?",
                    (remote_port, switch_id, now, existing_link['id'])
                )
            else:
                conn.execute(
                    """INSERT INTO links (local_switch_id, local_port, remote_chassis_id,
                       remote_port, remote_switch_id, first_seen, last_seen)
                       VALUES (0, ?, ?, ?, ?, ?, ?)""",
                    (local_port, chassis_id, remote_port, switch_id, now, now)
                )

    conn.commit()
    conn.close()


if __name__ == '__main__':
    poll_lldp()
