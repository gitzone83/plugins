"""Base vendor class providing default (generic) behavior for all vendors."""

import re

from lib.snmp_client import get_vlan_info as _get_vlan_info_qbridge

IF_TYPE_ETHERNET = 6       # ethernetCsmacd
IF_TYPE_LAG = 161           # ieee8023adLag


class VendorBase:
    """Default vendor behavior. Subclass and override only what differs."""

    VENDOR_NAME = 'generic'

    def is_visible_port(self, port_name, if_type=None):
        """Show ethernet (ifType 6) and LAG (ifType 161) interfaces.

        Falls back to showing everything if if_type is unavailable.
        """
        if if_type is None:
            return bool(port_name)
        return if_type in (IF_TYPE_ETHERNET, IF_TYPE_LAG)

    def short_port_name(self, port_name):
        """Return an abbreviated, vendor-neutral port name for display.

        Default: return as-is. Subclasses override for vendor-specific
        abbreviations.
        """
        return port_name or ''

    def map_lldp_to_ifindex(self, lldp_neighbors, address, credential):
        """Map LLDP localPortNum keys to ifIndex keys via lldpLocPortTable.

        Walks lldpLocPortId and correlates with ifName/ifDescr to build
        the mapping. Falls back to identity if the walk fails.
        """
        if not lldp_neighbors:
            return lldp_neighbors

        from lib.snmp_client import build_lldp_ifindex_map
        port_map = build_lldp_ifindex_map(address, credential)

        if not port_map:
            return lldp_neighbors

        remapped = {}
        for local_port_num, value in lldp_neighbors.items():
            if_index = port_map.get(local_port_num, local_port_num)
            remapped[if_index] = value
        return remapped

    def get_vlan_info(self, address, credential):
        """Retrieve per-interface VLAN info via Q-BRIDGE-MIB."""
        return _get_vlan_info_qbridge(address, credential)

    def get_model(self, address, credential, sys_descr):
        """Return hardware model string.

        Default: extract from sysDescr via parse_sys_descr().
        Subclasses can override to query ENTITY-MIB or other sources.
        """
        model, _ = self.parse_sys_descr(sys_descr)
        return model

    def parse_sys_descr(self, sys_descr):
        """Extract model and firmware version from sysDescr.

        Returns (model, firmware_version) tuple.
        Default: tries common patterns, falls back to truncated sysDescr.
        """
        if not sys_descr:
            return (None, None)
        # FreeBSD: "FreeBSD 14.3-RELEASE amd64 running on ..."
        m = re.match(r'(FreeBSD)\s+(\S+)', sys_descr)
        if m:
            return (m.group(1), m.group(2))
        # Linux: "Linux hostname 5.15.0 ..."
        m = re.match(r'(Linux)\s+\S+\s+(\S+)', sys_descr)
        if m:
            return (m.group(1), m.group(2))
        # Truncate raw sysDescr to something reasonable
        return (sys_descr[:64].split(',')[0].strip(), None)
