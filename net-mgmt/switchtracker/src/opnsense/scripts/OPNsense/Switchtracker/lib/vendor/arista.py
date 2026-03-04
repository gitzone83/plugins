"""Arista Networks (EOS) vendor handler."""

import re

from lib.vendor._base import VendorBase

_VISIBLE_PREFIXES = ('Ethernet', 'Port-Channel')


class AristaVendor(VendorBase):
    """Arista EOS specific behavior.

    - Port visibility: Ethernet and Port-Channel; exclude Management/Loopback/Vlan
    - LLDP mapping: uses default lldpLocPortTable walk
    - VLAN: standard Q-BRIDGE-MIB works on Arista
    """

    VENDOR_NAME = 'Arista'

    def short_port_name(self, port_name):
        """Normalize Arista port names.

        Arista uses 'Ethernet1' or 'Ethernet1/1' for all speeds.
        We can't determine speed class from the name alone, so use
        a generic 'ETH' prefix. Port-Channel becomes LAG.
        """
        if not port_name:
            return ''
        if port_name.startswith('Port-Channel'):
            return 'LAG ' + port_name[len('Port-Channel'):]
        if port_name.startswith('Ethernet'):
            return 'ETH ' + port_name[len('Ethernet'):]
        return port_name

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
