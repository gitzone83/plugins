"""SNMP client wrapper - shells out to net-snmp command-line tools."""

import re
import subprocess


# Standard SNMP OIDs
OID_SYSNAME = '1.3.6.1.2.1.1.5.0'
OID_SYSDESCR = '1.3.6.1.2.1.1.1.0'
OID_IF_INDEX = '1.3.6.1.2.1.2.2.1.1'
OID_IF_DESCR = '1.3.6.1.2.1.2.2.1.2'
OID_IF_ADMIN_STATUS = '1.3.6.1.2.1.2.2.1.7'
OID_IF_OPER_STATUS = '1.3.6.1.2.1.2.2.1.8'
OID_IF_SPEED = '1.3.6.1.2.1.2.2.1.5'
OID_IF_HIGH_SPEED = '1.3.6.1.2.1.31.1.1.1.15'
OID_IF_IN_OCTETS = '1.3.6.1.2.1.2.2.1.10'
OID_IF_OUT_OCTETS = '1.3.6.1.2.1.2.2.1.16'
OID_IF_IN_ERRORS = '1.3.6.1.2.1.2.2.1.14'
OID_IF_OUT_ERRORS = '1.3.6.1.2.1.2.2.1.20'
OID_IF_IN_UCAST_PKTS = '1.3.6.1.2.1.2.2.1.11'
OID_IF_OUT_UCAST_PKTS = '1.3.6.1.2.1.2.2.1.17'
OID_IF_TYPE = '1.3.6.1.2.1.2.2.1.3'
OID_IF_NAME = '1.3.6.1.2.1.31.1.1.1.1'

# LLDP-MIB OIDs (indexed by timeMark.localPortNum.remIndex)
OID_LLDP_REM_SYS_NAME = '1.0.8802.1.1.2.1.4.1.1.9'
OID_LLDP_REM_PORT_ID = '1.0.8802.1.1.2.1.4.1.1.7'
OID_LLDP_REM_PORT_DESC = '1.0.8802.1.1.2.1.4.1.1.8'
OID_LLDP_LOC_PORT_ID = '1.0.8802.1.1.2.1.3.7.1.3'

# Q-BRIDGE-MIB OIDs for VLAN info
OID_DOT1Q_PVID = '1.3.6.1.2.1.17.7.1.4.5.1.1'           # Access/native VLAN per bridge port
OID_DOT1D_BASE_PORT_IFINDEX = '1.3.6.1.2.1.17.1.4.1.2'   # Bridge port -> ifIndex mapping
OID_DOT1Q_VLAN_STATIC_NAME = '1.3.6.1.2.1.17.7.1.4.3.1.1'  # VLAN ID -> name

ADMIN_STATUS_MAP = {'1': 'up', '2': 'down', '3': 'testing'}
OPER_STATUS_MAP = {'1': 'up', '2': 'down', '3': 'testing', '4': 'unknown',
                   '5': 'dormant', '6': 'notPresent', '7': 'lowerLayerDown'}


def _build_snmp_args(address, credential):
    """Build snmpwalk/snmpget command arguments from a credential dict."""
    version = credential.get('version', '2c')
    args = ['-v', version]

    if version == '2c':
        community = credential.get('community', 'public')
        args.extend(['-c', community])
    elif version == 'v3' or version == '3':
        args.extend(['-u', credential.get('v3Username', '')])
        sec_level = credential.get('v3SecurityLevel', 'authPriv')
        args.extend(['-l', sec_level])

        if sec_level in ('authNoPriv', 'authPriv'):
            auth_proto = credential.get('v3AuthProto', 'SHA')
            args.extend(['-a', auth_proto])
            args.extend(['-A', credential.get('v3AuthKey', '')])

        if sec_level == 'authPriv':
            priv_proto = credential.get('v3PrivProto', 'AES')
            args.extend(['-x', priv_proto])
            args.extend(['-X', credential.get('v3PrivKey', '')])

    args.append(address)
    return args


def snmpget(address, credential, oid):
    """Run snmpget and return the value string, or None on failure."""
    args = ['snmpget', '-Oqv'] + _build_snmp_args(address, credential) + [oid]
    try:
        result = subprocess.run(args, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            value = result.stdout.strip().strip('"')
            if value and 'No Such' not in value:
                return value
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return None


def snmpwalk(address, credential, oid):
    """Run snmpwalk and return a dict of {index: value}.

    Index is extracted from the last component of the returned OID.
    Uses -e flag for numeric enum output (e.g. ifType returns 6 not 'ethernetCsmacd').
    """
    args = ['snmpwalk', '-Oqne'] + _build_snmp_args(address, credential) + [oid]
    try:
        result = subprocess.run(args, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            return {}
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return {}

    values = {}
    for line in result.stdout.strip().split('\n'):
        if not line:
            continue
        parts = line.split(None, 1)
        if len(parts) < 2:
            continue
        oid_str = parts[0]
        value = parts[1].strip().strip('"')
        # Extract last OID component as index
        match = re.search(r'\.(\d+)$', oid_str)
        if match:
            values[match.group(1)] = value

    return values


def _snmpwalk_lldp(address, credential, oid):
    """Walk an LLDP-MIB table and return {localPortNum: value}.

    LLDP remote tables are indexed by timeMark.localPortNum.remIndex.
    We extract localPortNum (second-to-last component) as the key.
    If multiple neighbors exist on a port, the last one wins.
    """
    args = ['snmpwalk', '-Oqn'] + _build_snmp_args(address, credential) + [oid]
    try:
        result = subprocess.run(args, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            return {}
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return {}

    values = {}
    for line in result.stdout.strip().split('\n'):
        if not line:
            continue
        parts = line.split(None, 1)
        if len(parts) < 2:
            continue
        oid_str = parts[0]
        value = parts[1].strip().strip('"')
        # LLDP index: ...oid.timeMark.localPortNum.remIndex
        # Extract the three trailing components
        match = re.search(r'\.(\d+)\.(\d+)\.(\d+)$', oid_str)
        if match:
            local_port_num = match.group(2)
            values[local_port_num] = value

    return values


def get_lldp_neighbors(address, credential):
    """Get LLDP neighbor info per port.

    Returns {localPortNum_str: {'name': str, 'port': str}}.
    Keys are lldpRemLocalPortNum values, which may NOT equal ifIndex
    on all vendors. Use vendor.map_lldp_to_ifindex() to remap.
    """
    sys_names = _snmpwalk_lldp(address, credential, OID_LLDP_REM_SYS_NAME)
    port_ids = _snmpwalk_lldp(address, credential, OID_LLDP_REM_PORT_ID)
    port_descs = _snmpwalk_lldp(address, credential, OID_LLDP_REM_PORT_DESC)

    neighbors = {}
    for idx in set(list(sys_names.keys()) + list(port_ids.keys())):
        name = sys_names.get(idx, '')
        port = port_descs.get(idx) or port_ids.get(idx, '')
        if name or port:
            neighbors[idx] = {'name': name, 'port': port}

    return neighbors


def get_vlan_info(address, credential):
    """Get access/native VLAN per interface via Q-BRIDGE-MIB.

    Returns {ifIndex_str: {'vlan_id': int, 'vlan_name': str}}.
    """
    # Map bridge port -> ifIndex
    bridge_to_if = snmpwalk(address, credential, OID_DOT1D_BASE_PORT_IFINDEX)
    # bridge_to_if: {bridgePort: ifIndex}

    # Get PVID per bridge port
    pvids = snmpwalk(address, credential, OID_DOT1Q_PVID)
    # pvids: {bridgePort: vlanId}

    # Get VLAN names
    vlan_names_raw = snmpwalk(address, credential, OID_DOT1Q_VLAN_STATIC_NAME)
    # vlan_names_raw: {vlanId: vlanName}

    vlans = {}
    for bridge_port, vlan_id_str in pvids.items():
        if_index = bridge_to_if.get(bridge_port, bridge_port)
        try:
            vlan_id = int(vlan_id_str)
        except (ValueError, TypeError):
            continue
        vlan_name = vlan_names_raw.get(vlan_id_str, '')
        vlans[if_index] = {'vlan_id': vlan_id, 'vlan_name': vlan_name}

    return vlans


def get_switch_ports(address, credential):
    """Poll all interface data for a switch via SNMP.

    Returns a list of dicts with port info.
    """
    indices = snmpwalk(address, credential, OID_IF_INDEX)
    if not indices:
        return []

    names = snmpwalk(address, credential, OID_IF_DESCR)
    admin_statuses = snmpwalk(address, credential, OID_IF_ADMIN_STATUS)
    oper_statuses = snmpwalk(address, credential, OID_IF_OPER_STATUS)
    # ifHighSpeed reports Mbps directly, no 32-bit wrap for 10G+ links
    high_speeds = snmpwalk(address, credential, OID_IF_HIGH_SPEED)
    speeds = snmpwalk(address, credential, OID_IF_SPEED) if not high_speeds else {}
    if_types = snmpwalk(address, credential, OID_IF_TYPE)
    in_octets = snmpwalk(address, credential, OID_IF_IN_OCTETS)
    out_octets = snmpwalk(address, credential, OID_IF_OUT_OCTETS)
    in_errors = snmpwalk(address, credential, OID_IF_IN_ERRORS)
    out_errors = snmpwalk(address, credential, OID_IF_OUT_ERRORS)
    in_pkts = snmpwalk(address, credential, OID_IF_IN_UCAST_PKTS)
    out_pkts = snmpwalk(address, credential, OID_IF_OUT_UCAST_PKTS)

    ports = []
    for idx in sorted(indices.keys(), key=int):
        admin_val = admin_statuses.get(idx, '')
        oper_val = oper_statuses.get(idx, '')

        # Prefer ifHighSpeed (Mbps), fall back to ifSpeed (bps / 1000000)
        if high_speeds:
            try:
                speed_mbps = int(high_speeds.get(idx, '0') or '0')
            except (ValueError, TypeError):
                speed_mbps = 0
        else:
            try:
                speed_mbps = int(speeds.get(idx, '0') or '0') // 1000000
            except (ValueError, TypeError):
                speed_mbps = 0

        try:
            if_type = int(if_types.get(idx, '0') or '0')
        except (ValueError, TypeError):
            if_type = 0

        ports.append({
            'port_index': int(idx),
            'port_name': names.get(idx, ''),
            'if_type': if_type,
            'admin_status': ADMIN_STATUS_MAP.get(admin_val, admin_val),
            'oper_status': OPER_STATUS_MAP.get(oper_val, oper_val),
            'speed_mbps': speed_mbps,
            'in_octets': int(in_octets.get(idx, 0) or 0),
            'out_octets': int(out_octets.get(idx, 0) or 0),
            'in_pkts': int(in_pkts.get(idx, 0) or 0),
            'out_pkts': int(out_pkts.get(idx, 0) or 0),
            'in_errors': int(in_errors.get(idx, 0) or 0),
            'out_errors': int(out_errors.get(idx, 0) or 0),
        })

    return ports


def build_lldp_ifindex_map(address, credential):
    """Build a mapping from LLDP localPortNum to ifIndex.

    Walks lldpLocPortId (indexed by localPortNum, values are port identifiers)
    and ifName (indexed by ifIndex), then correlates the two.

    Returns {localPortNum_str: ifIndex_str}, or empty dict on failure.
    """
    # lldpLocPortId: {localPortNum: portIdStr}
    loc_port_ids = snmpwalk(address, credential, OID_LLDP_LOC_PORT_ID)
    if not loc_port_ids:
        return {}

    # ifName: {ifIndex: ifNameStr}
    if_names = snmpwalk(address, credential, OID_IF_NAME)
    # ifDescr: {ifIndex: ifDescrStr}
    if_descrs = snmpwalk(address, credential, OID_IF_DESCR)

    # Build reverse lookup: name/descr -> ifIndex
    name_to_ifindex = {}
    for if_idx, name in if_names.items():
        name_to_ifindex[name] = if_idx
    for if_idx, descr in if_descrs.items():
        if descr not in name_to_ifindex:
            name_to_ifindex[descr] = if_idx

    port_map = {}
    for local_port_num, port_id in loc_port_ids.items():
        if port_id in name_to_ifindex:
            port_map[local_port_num] = name_to_ifindex[port_id]
        else:
            # Fall back to identity
            port_map[local_port_num] = local_port_num

    return port_map
