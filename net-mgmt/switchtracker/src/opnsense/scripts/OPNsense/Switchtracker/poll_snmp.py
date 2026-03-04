#!/usr/local/bin/python3
"""Poll switches via SNMP and update port status in SQLite."""

import time
from lib.db import get_connection
from lib.config_reader import read_config, get_credential_by_uuid
from lib.snmp_client import (get_switch_ports, get_lldp_neighbors,
                              snmpget, OID_SYSNAME, OID_SYSDESCR)
from lib.vendor import get_vendor_handler


def _poll_switch(conn, config, sw):
    """Poll a single configured switch and update the database."""
    now = time.time()

    if sw.get('enabled', '0') != '1':
        return
    if sw.get('snmpEnabled', '0') != '1':
        return

    address = sw.get('address', '')
    if not address:
        return

    cred_uuid = sw.get('credential', '')
    credential = get_credential_by_uuid(config, cred_uuid) or {}
    if credential.get('enabled', '1') == '0':
        return

    # Try to get sysName and sysDescr
    sys_name = snmpget(address, credential, OID_SYSNAME)
    sys_descr = snmpget(address, credential, OID_SYSDESCR)

    # Detect vendor from sysDescr
    vendor = get_vendor_handler(sys_descr)

    # Get model (vendor-specific: may query ENTITY-MIB) and firmware
    model = vendor.get_model(address, credential, sys_descr)
    _, firmware = vendor.parse_sys_descr(sys_descr)

    # Find or create switch in SQLite by address
    chassis_id = address
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
               vendor = ?, last_seen = ?, is_online = 1, config_uuid = ?
               WHERE id = ?""",
            (hostname, address, model, firmware,
             vendor.VENDOR_NAME, now, sw.get('uuid', ''), switch_id)
        )
    else:
        cursor = conn.execute(
            """INSERT INTO switches (chassis_id, hostname, mgmt_ip, model,
               firmware_version, vendor, source, config_uuid,
               first_seen, last_seen, is_online)
               VALUES (?, ?, ?, ?, ?, ?, 'manual', ?, ?, ?, 1)""",
            (chassis_id, hostname, address, model, firmware,
             vendor.VENDOR_NAME, sw.get('uuid', ''), now, now)
        )
        switch_id = cursor.lastrowid

    # Poll ports
    ports = get_switch_ports(address, credential)

    # Poll LLDP neighbors (keyed by localPortNum) and remap to ifIndex
    raw_lldp_neighbors = get_lldp_neighbors(address, credential)
    lldp_neighbors = vendor.map_lldp_to_ifindex(raw_lldp_neighbors, address, credential)

    # Poll VLAN info via vendor-specific method
    vlan_info = vendor.get_vlan_info(address, credential)

    for port in ports:
        idx_str = str(port['port_index'])
        neighbor = lldp_neighbors.get(idx_str, {})
        vlan = vlan_info.get(idx_str, {})

        existing_port = conn.execute(
            "SELECT id FROM ports WHERE switch_id = ? AND port_index = ?",
            (switch_id, port['port_index'])
        ).fetchone()

        if existing_port:
            conn.execute(
                """UPDATE ports SET port_name = ?, if_type = ?,
                   admin_status = ?, oper_status = ?,
                   speed_mbps = ?, in_octets = ?, out_octets = ?,
                   in_pkts = ?, out_pkts = ?,
                   in_errors = ?, out_errors = ?,
                   lldp_neighbor_name = ?, lldp_neighbor_port = ?,
                   vlan_id = ?, vlan_name = ?,
                   last_updated = ?
                   WHERE id = ?""",
                (port['port_name'], port['if_type'],
                 port['admin_status'], port['oper_status'],
                 port['speed_mbps'], port['in_octets'], port['out_octets'],
                 port['in_pkts'], port['out_pkts'],
                 port['in_errors'], port['out_errors'],
                 neighbor.get('name', ''), neighbor.get('port', ''),
                 vlan.get('vlan_id'), vlan.get('vlan_name', ''),
                 now, existing_port['id'])
            )
        else:
            conn.execute(
                """INSERT INTO ports (switch_id, port_index, port_name, if_type,
                   admin_status, oper_status, speed_mbps,
                   in_octets, out_octets, in_pkts, out_pkts,
                   in_errors, out_errors,
                   lldp_neighbor_name, lldp_neighbor_port,
                   vlan_id, vlan_name, last_updated)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (switch_id, port['port_index'], port['port_name'], port['if_type'],
                 port['admin_status'], port['oper_status'], port['speed_mbps'],
                 port['in_octets'], port['out_octets'],
                 port['in_pkts'], port['out_pkts'],
                 port['in_errors'], port['out_errors'],
                 neighbor.get('name', ''), neighbor.get('port', ''),
                 vlan.get('vlan_id'), vlan.get('vlan_name', ''),
                 now)
            )

    conn.commit()


def poll_snmp(target_uuid=None):
    """Poll configured switches that have SNMP enabled.

    If target_uuid is given, only poll the switch with that config UUID.
    """
    config = read_config()
    conn = get_connection()

    for sw in config.get('switches', []):
        if target_uuid and sw.get('uuid', '') != target_uuid:
            continue
        _poll_switch(conn, config, sw)

    conn.close()


if __name__ == '__main__':
    poll_snmp()
