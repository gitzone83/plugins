"""Cisco NX-OS (Nexus) vendor handler."""

from lib.vendor._base import VendorBase

_VISIBLE_PREFIXES = ('Ethernet', 'port-channel')


class CiscoNXOSVendor(VendorBase):
    """Cisco NX-OS specific behavior.

    - Port visibility: Ethernet and port-channel; exclude mgmt/loopback/Vlan/nve
    - LLDP mapping: uses default lldpLocPortTable walk
    - VLAN: standard Q-BRIDGE-MIB works on NX-OS
    """

    VENDOR_NAME = 'Cisco'

    def short_port_name(self, port_name):
        """Normalize NX-OS port names.

        NX-OS uses 'Ethernet1/1' for all speeds. Use generic 'ETH' prefix.
        port-channel becomes LAG.
        """
        if not port_name:
            return ''
        if port_name.startswith('port-channel'):
            return 'LAG ' + port_name[len('port-channel'):]
        if port_name.startswith('Ethernet'):
            return 'ETH ' + port_name[len('Ethernet'):]
        return port_name

    def is_visible_port(self, port_name, if_type=None):
        if not port_name:
            return False
        if port_name.startswith(_VISIBLE_PREFIXES):
            return True
        if if_type is not None:
            return super().is_visible_port(port_name, if_type)
        return False
