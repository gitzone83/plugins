#!/usr/local/bin/python3
"""Poll switches via SNMP and update port status in SQLite."""

import time
from lib.db import get_connection
from lib.config_reader import read_config, get_credential_by_uuid
from lib.snmp_client import get_switch_ports, snmpget, OID_SYSNAME, OID_SYSDESCR


def poll_snmp():
    """Poll all configured switches that have SNMP enabled."""
    config = read_config()
    conn = get_connection()
    now = time.time()

    for sw in config.get('switches', []):
        if sw.get('enabled', '0') != '1':
            continue
        if sw.get('snmpEnabled', '0') != '1':
            continue

        address = sw.get('address', '')
        if not address:
            continue

        cred_uuid = sw.get('credential', '')
        credential = get_credential_by_uuid(config, cred_uuid) or {}
        if credential.get('enabled', '1') == '0':
            continue

        # Try to get sysName and sysDescr
        sys_name = snmpget(address, credential, OID_SYSNAME)
        sys_descr = snmpget(address, credential, OID_SYSDESCR)

        # Find or create switch in SQLite by address
        # Use hostname from config or SNMP sysName as chassis_id fallback
        chassis_id = address  # Use address as chassis_id for manually configured switches
        hostname = sw.get('hostname', '') or sys_name or address

        existing = conn.execute(
            "SELECT id FROM switches WHERE chassis_id = ? OR mgmt_ip = ?",
            (chassis_id, address)
        ).fetchone()

        if existing:
            switch_id = existing['id']
            conn.execute(
                """UPDATE switches SET hostname = ?, mgmt_ip = ?,
                   model = COALESCE(?, model), firmware_version = COALESCE(?, firmware_version),
                   last_seen = ?, is_online = 1, config_uuid = ?
                   WHERE id = ?""",
                (hostname, address, sys_descr, None, now, sw.get('uuid', ''), switch_id)
            )
        else:
            cursor = conn.execute(
                """INSERT INTO switches (chassis_id, hostname, mgmt_ip, model,
                   source, config_uuid, first_seen, last_seen, is_online)
                   VALUES (?, ?, ?, ?, 'manual', ?, ?, ?, 1)""",
                (chassis_id, hostname, address, sys_descr, sw.get('uuid', ''), now, now)
            )
            switch_id = cursor.lastrowid

        # Poll ports
        ports = get_switch_ports(address, credential)
        for port in ports:
            existing_port = conn.execute(
                "SELECT id FROM ports WHERE switch_id = ? AND port_index = ?",
                (switch_id, port['port_index'])
            ).fetchone()

            if existing_port:
                conn.execute(
                    """UPDATE ports SET port_name = ?, admin_status = ?, oper_status = ?,
                       speed_mbps = ?, in_octets = ?, out_octets = ?,
                       in_errors = ?, out_errors = ?, last_updated = ?
                       WHERE id = ?""",
                    (port['port_name'], port['admin_status'], port['oper_status'],
                     port['speed_mbps'], port['in_octets'], port['out_octets'],
                     port['in_errors'], port['out_errors'], now, existing_port['id'])
                )
            else:
                conn.execute(
                    """INSERT INTO ports (switch_id, port_index, port_name, admin_status,
                       oper_status, speed_mbps, in_octets, out_octets,
                       in_errors, out_errors, last_updated)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (switch_id, port['port_index'], port['port_name'],
                     port['admin_status'], port['oper_status'], port['speed_mbps'],
                     port['in_octets'], port['out_octets'],
                     port['in_errors'], port['out_errors'], now)
                )

        conn.commit()

    conn.close()


if __name__ == '__main__':
    poll_snmp()
