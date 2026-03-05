#!/bin/sh
#
# Uninstall os-switchtracker plugin from OPNsense
#
# Usage (run as root on OPNsense via SSH):
#   fetch -o /tmp/uninstall.sh https://raw.githubusercontent.com/gitzone83/plugins/feature/os-switchtracker/net-mgmt/switchtracker/scripts/uninstall.sh
#   sh /tmp/uninstall.sh
#

set -e

LOCALBASE="/usr/local"

if [ "$(id -u)" -ne 0 ]; then
    echo "Error: this script must be run as root."
    exit 1
fi

echo ">>> Removing os-switchtracker..."

# Remove plugin files
rm -f "${LOCALBASE}/etc/inc/plugins.inc.d/switchtracker.inc"
rm -rf "${LOCALBASE}/opnsense/mvc/app/controllers/OPNsense/Switchtracker"
rm -rf "${LOCALBASE}/opnsense/mvc/app/models/OPNsense/Switchtracker"
rm -rf "${LOCALBASE}/opnsense/mvc/app/views/OPNsense/Switchtracker"
rm -rf "${LOCALBASE}/opnsense/scripts/OPNsense/Switchtracker"
rm -f "${LOCALBASE}/opnsense/service/conf/actions.d/actions_switchtracker.conf"

# Restart configd
echo ">>> Restarting configd..."
service configd restart

echo ">>> os-switchtracker removed successfully."
