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
OID_IF_IN_OCTETS = '1.3.6.1.2.1.2.2.1.10'
OID_IF_OUT_OCTETS = '1.3.6.1.2.1.2.2.1.16'
OID_IF_IN_ERRORS = '1.3.6.1.2.1.2.2.1.14'
OID_IF_OUT_ERRORS = '1.3.6.1.2.1.2.2.1.20'

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
        # Extract last OID component as index
        match = re.search(r'\.(\d+)$', oid_str)
        if match:
            values[match.group(1)] = value

    return values


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
    speeds = snmpwalk(address, credential, OID_IF_SPEED)
    in_octets = snmpwalk(address, credential, OID_IF_IN_OCTETS)
    out_octets = snmpwalk(address, credential, OID_IF_OUT_OCTETS)
    in_errors = snmpwalk(address, credential, OID_IF_IN_ERRORS)
    out_errors = snmpwalk(address, credential, OID_IF_OUT_ERRORS)

    ports = []
    for idx in sorted(indices.keys(), key=int):
        admin_val = admin_statuses.get(idx, '')
        oper_val = oper_statuses.get(idx, '')
        speed_val = speeds.get(idx, '0')

        try:
            speed_mbps = int(speed_val) // 1000000
        except (ValueError, TypeError):
            speed_mbps = 0

        ports.append({
            'port_index': int(idx),
            'port_name': names.get(idx, ''),
            'admin_status': ADMIN_STATUS_MAP.get(admin_val, admin_val),
            'oper_status': OPER_STATUS_MAP.get(oper_val, oper_val),
            'speed_mbps': speed_mbps,
            'in_octets': int(in_octets.get(idx, 0) or 0),
            'out_octets': int(out_octets.get(idx, 0) or 0),
            'in_errors': int(in_errors.get(idx, 0) or 0),
            'out_errors': int(out_errors.get(idx, 0) or 0),
        })

    return ports
