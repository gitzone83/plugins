"""Arista Networks (EOS) vendor handler."""

from lib.vendor._base import VendorBase

_VISIBLE_PREFIXES = ('Ethernet', 'Port-Channel')


class AristaVendor(VendorBase):
    """Arista EOS specific behavior.

    - Port visibility: Ethernet and Port-Channel; exclude Management/Loopback/Vlan
    - LLDP mapping: uses default lldpLocPortTable walk
    - VLAN: standard Q-BRIDGE-MIB works on Arista
    """

    VENDOR_NAME = 'Arista'

    def is_visible_port(self, port_name, if_type=None):
        if not port_name:
            return False
        if port_name.startswith(_VISIBLE_PREFIXES):
            # Exclude sub-interfaces (Ethernet1.100)
            if '.' in port_name:
                return False
            return True
        if if_type is not None:
            return super().is_visible_port(port_name, if_type)
        return False
