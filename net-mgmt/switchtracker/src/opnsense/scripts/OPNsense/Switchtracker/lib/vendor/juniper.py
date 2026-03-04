"""Juniper Networks vendor handler."""

import re

from lib.vendor._base import VendorBase

_VISIBLE_PREFIXES = ('xe-', 'ge-', 'ae', 'et-', 'irb')


class JuniperVendor(VendorBase):
    """Juniper-specific behavior.

    - Port visibility: prefix-based, exclude .N sub-interfaces
    - LLDP mapping: localPortNum == ifIndex (identity, no extra walk)
    - VLAN: standard Q-BRIDGE-MIB works
    """

    VENDOR_NAME = 'Juniper'

    def is_visible_port(self, port_name, if_type=None):
        if not port_name:
            return False
        if not port_name.startswith(_VISIBLE_PREFIXES):
            return False
        if '.' in port_name:
            return False
        return True

    def map_lldp_to_ifindex(self, lldp_neighbors, address, credential):
        """Identity mapping -- on Juniper, localPortNum == ifIndex."""
        return lldp_neighbors

    def parse_sys_descr(self, sys_descr):
        """Parse Juniper sysDescr.

        Example: 'Juniper Networks, Inc. qfx5110-48s-4c Ethernet Switch,
                  kernel JUNOS 21.2X4.2, Build date: ...'
        Returns: ('QFX5110-48S-4C', '21.2X4.2')
        """
        if not sys_descr:
            return (None, None)
        # Model: word after "Inc. " and before " Ethernet Switch" or ","
        model_match = re.search(r'Inc\.\s+(\S+)', sys_descr)
        model = model_match.group(1).upper() if model_match else None
        # Firmware: JUNOS version
        ver_match = re.search(r'JUNOS\s+(\S+)', sys_descr)
        firmware = ver_match.group(1).rstrip(',') if ver_match else None
        return (model, firmware)
