"""Cisco IOS / IOS-XE vendor handler."""

import re

from lib.vendor._base import VendorBase
from lib.snmp_client import snmpget, snmpwalk

_VISIBLE_PREFIXES = ('GigabitEthernet', 'TenGigabitEthernet',
                     'TwentyFiveGigE', 'FortyGigabitEthernet',
                     'HundredGigE', 'Port-channel')

# Cisco-proprietary OIDs for VLAN fallback
OID_VM_VLAN = '1.3.6.1.4.1.9.9.68.1.2.2.1.2'              # vmVlan per ifIndex
OID_VTP_VLAN_NAME = '1.3.6.1.4.1.9.9.46.1.3.1.1.4.1'      # vtpVlanName (domain 1)


class CiscoIOSVendor(VendorBase):
    """Cisco IOS / IOS-XE specific behavior.

    - Port visibility: physical + Port-channel, exclude Vlan/Loopback/Null/Tunnel
    - LLDP mapping: uses default lldpLocPortTable walk
    - VLAN: Q-BRIDGE-MIB first, then CISCO-VTP-MIB fallback
    """

    VENDOR_NAME = 'Cisco'

    def is_visible_port(self, port_name, if_type=None):
        if not port_name:
            return False
        if port_name.startswith(_VISIBLE_PREFIXES):
            return True
        # Fall back to ifType for unknown names
        if if_type is not None:
            return super().is_visible_port(port_name, if_type)
        return False

    # ENTITY-MIB: entPhysicalModelName (chassis = index 1)
    OID_ENT_MODEL = '1.3.6.1.2.1.47.1.1.1.1.13.1'

    def get_model(self, address, credential, sys_descr):
        """Get hardware model from ENTITY-MIB, fall back to sysDescr."""
        model = snmpget(address, credential, self.OID_ENT_MODEL)
        if model:
            return model
        model, _ = self.parse_sys_descr(sys_descr)
        return model

    def get_vlan_info(self, address, credential):
        """Try Q-BRIDGE-MIB first, fall back to Cisco VTP/VM MIBs."""
        result = super().get_vlan_info(address, credential)
        if result:
            return result

        # Fallback: CISCO-VLAN-MEMBERSHIP-MIB vmVlan
        vm_vlans = snmpwalk(address, credential, OID_VM_VLAN)
        if not vm_vlans:
            return {}

        # Get VLAN names from VTP
        vlan_names = snmpwalk(address, credential, OID_VTP_VLAN_NAME)

        vlans = {}
        for if_index, vlan_id_str in vm_vlans.items():
            try:
                vlan_id = int(vlan_id_str)
            except (ValueError, TypeError):
                continue
            vlan_name = vlan_names.get(vlan_id_str, '')
            vlans[if_index] = {'vlan_id': vlan_id, 'vlan_name': vlan_name}

        return vlans

    def parse_sys_descr(self, sys_descr):
        """Parse Cisco IOS/IOS-XE sysDescr.

        Example: 'Cisco IOS Software, C3750E Software (C3750E-UNIVERSALK9-M),
                  Version 15.2(4)E10, ...'
        Returns: ('C3750E', '15.2(4)E10')

        IOS-XE example: 'Cisco IOS Software, IOS-XE Software, Catalyst L3
                  Switch Software (CAT3K_CAA-UNIVERSALK9-M), Version 03.07.05E ...'
        Returns: ('CAT3K_CAA', '03.07.05E')
        """
        if not sys_descr:
            return (None, None)
        # Extract platform/image name from parenthesized image string
        # e.g. (C3750E-UNIVERSALK9-M) → C3750E
        # e.g. (CAT3K_CAA-UNIVERSALK9-M) → CAT3K_CAA
        image_match = re.search(r'\(([A-Za-z0-9_]+)-', sys_descr)
        model = image_match.group(1) if image_match else None
        ver_match = re.search(r'Version\s+(\S+)', sys_descr)
        firmware = ver_match.group(1).rstrip(',') if ver_match else None
        return (model, firmware)
