"""Parse LLDP neighbor data from lldpcli."""

import json
import subprocess


def get_lldp_neighbors():
    """Run lldpcli and return parsed neighbor list.

    Returns a list of dicts with keys:
        chassis_id, hostname, mgmt_ip, mac_address, model,
        local_port, remote_port
    """
    try:
        result = subprocess.run(
            ['lldpcli', '-f', 'json', 'show', 'neighbors'],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            return []
        data = json.loads(result.stdout)
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
        return []

    neighbors = []
    lldp = data.get('lldp', {})

    # lldpcli JSON structure: lldp.interface.[iface_name].port/chassis
    interfaces = lldp.get('interface', {})
    if isinstance(interfaces, list):
        iface_list = interfaces
    else:
        iface_list = [interfaces]

    for iface_block in iface_list:
        if not isinstance(iface_block, dict):
            continue
        for local_iface, iface_data in iface_block.items():
            if not isinstance(iface_data, dict):
                continue

            chassis_data = iface_data.get('chassis', {})
            port_data = iface_data.get('port', {})

            # chassis may be nested under a hostname key
            if isinstance(chassis_data, dict):
                for chassis_key, chassis_info in chassis_data.items():
                    if isinstance(chassis_info, dict):
                        chassis_data = chassis_info
                        break

            chassis_id_info = chassis_data.get('id', {})
            if isinstance(chassis_id_info, dict):
                chassis_id = chassis_id_info.get('value', '')
            else:
                chassis_id = str(chassis_id_info) if chassis_id_info else ''

            if not chassis_id:
                continue

            hostname = chassis_data.get('name', '')
            descr = chassis_data.get('descr', '')

            # Management IP
            mgmt_ip = ''
            mgmt_info = chassis_data.get('mgmt-ip', '')
            if isinstance(mgmt_info, list):
                mgmt_ip = mgmt_info[0] if mgmt_info else ''
            elif isinstance(mgmt_info, str):
                mgmt_ip = mgmt_info

            # MAC address from chassis ID if type is mac
            mac_address = ''
            if isinstance(chassis_id_info, dict) and chassis_id_info.get('type', '') == 'mac':
                mac_address = chassis_id

            # Remote port
            port_id_info = port_data.get('id', {})
            if isinstance(port_id_info, dict):
                remote_port = port_id_info.get('value', '')
            else:
                remote_port = str(port_id_info) if port_id_info else ''

            neighbors.append({
                'chassis_id': chassis_id,
                'hostname': hostname or chassis_id,
                'mgmt_ip': mgmt_ip,
                'mac_address': mac_address,
                'model': descr,
                'local_port': local_iface,
                'remote_port': remote_port,
            })

    return neighbors
