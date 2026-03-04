"""Vendor detection and module dispatch.

Usage:
    from lib.vendor import get_vendor_handler
    vendor = get_vendor_handler(sys_descr)
    visible = vendor.is_visible_port(port_name, if_type)
"""

from lib.vendor._base import VendorBase
from lib.vendor.juniper import JuniperVendor
from lib.vendor.cisco_ios import CiscoIOSVendor
from lib.vendor.cisco_nxos import CiscoNXOSVendor
from lib.vendor.arista import AristaVendor

# Detection rules: (substring_in_sysDescr, vendor_class)
# Order matters: more specific matches first.
_VENDOR_RULES = [
    ('Juniper',     JuniperVendor),
    ('NX-OS',       CiscoNXOSVendor),
    ('Arista',      AristaVendor),
    ('Cisco IOS',   CiscoIOSVendor),
    ('IOS-XE',      CiscoIOSVendor),
    ('Cisco',       CiscoIOSVendor),
]

_KEY_TO_CLASS = {
    'Juniper':      JuniperVendor,
    'Cisco':        CiscoIOSVendor,
    'Arista':       AristaVendor,
    'generic':      VendorBase,
    # Legacy keys for backward compatibility
    'Cisco IOS':    CiscoIOSVendor,
    'Cisco NX-OS':  CiscoNXOSVendor,
    'juniper':      JuniperVendor,
    'cisco_ios':    CiscoIOSVendor,
    'cisco_nxos':   CiscoNXOSVendor,
    'arista':       AristaVendor,
}

_CACHE = {}


def get_vendor_handler(sys_descr):
    """Return a vendor handler instance based on sysDescr string."""
    matched_cls = VendorBase
    if sys_descr:
        for pattern, cls in _VENDOR_RULES:
            if pattern in sys_descr:
                matched_cls = cls
                break

    cache_key = matched_cls.__name__
    if cache_key not in _CACHE:
        _CACHE[cache_key] = matched_cls()
    return _CACHE[cache_key]


def get_vendor_handler_by_key(vendor_key):
    """Return a vendor handler by its stored key (e.g. 'juniper')."""
    if not vendor_key:
        vendor_key = 'generic'
    if vendor_key not in _CACHE:
        cls = _KEY_TO_CLASS.get(vendor_key, VendorBase)
        _CACHE[vendor_key] = cls()
    return _CACHE[vendor_key]
