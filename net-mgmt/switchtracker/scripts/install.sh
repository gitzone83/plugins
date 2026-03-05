#!/bin/sh
#
# Install os-switchtracker plugin for OPNsense
#
# Usage (run as root on OPNsense via SSH):
#   fetch -o /tmp/install.sh https://raw.githubusercontent.com/gitzone83/plugins/feature/os-switchtracker/net-mgmt/switchtracker/scripts/install.sh
#   sh /tmp/install.sh
#

set -e

REPO="gitzone83/plugins"
BRANCH="feature/os-switchtracker"
PLUGIN_DIR="net-mgmt/switchtracker"
LOCALBASE="/usr/local"
BASEURL="https://raw.githubusercontent.com/${REPO}/${BRANCH}/${PLUGIN_DIR}/src"

if [ "$(id -u)" -ne 0 ]; then
    echo "Error: this script must be run as root."
    exit 1
fi

if ! command -v configctl >/dev/null 2>&1; then
    echo "Error: this does not appear to be an OPNsense system."
    exit 1
fi

# Check dependencies
for dep in lldpd net-snmp; do
    if ! pkg info "os-${dep}" >/dev/null 2>&1 && ! pkg info "${dep}" >/dev/null 2>&1; then
        echo "Warning: dependency '${dep}' not found. Install os-lldpd and net-snmp first."
    fi
done

echo ">>> Fetching file list..."

# All plugin files relative to src/
FILES="
etc/inc/plugins.inc.d/switchtracker.inc
opnsense/mvc/app/controllers/OPNsense/Switchtracker/Api/ServiceController.php
opnsense/mvc/app/controllers/OPNsense/Switchtracker/Api/SettingsController.php
opnsense/mvc/app/controllers/OPNsense/Switchtracker/forms/dialogEditAlertRule.xml
opnsense/mvc/app/controllers/OPNsense/Switchtracker/forms/dialogEditCredential.xml
opnsense/mvc/app/controllers/OPNsense/Switchtracker/forms/dialogEditSwitch.xml
opnsense/mvc/app/controllers/OPNsense/Switchtracker/forms/general.xml
opnsense/mvc/app/controllers/OPNsense/Switchtracker/GeneralController.php
opnsense/mvc/app/models/OPNsense/Switchtracker/ACL/ACL.xml
opnsense/mvc/app/models/OPNsense/Switchtracker/Menu/Menu.xml
opnsense/mvc/app/models/OPNsense/Switchtracker/Switchtracker.php
opnsense/mvc/app/models/OPNsense/Switchtracker/Switchtracker.xml
opnsense/mvc/app/views/OPNsense/Switchtracker/general.volt
opnsense/scripts/OPNsense/Switchtracker/check_alerts.py
opnsense/scripts/OPNsense/Switchtracker/dump_ports.py
opnsense/scripts/OPNsense/Switchtracker/dump_switches.py
opnsense/scripts/OPNsense/Switchtracker/dump_topology.py
opnsense/scripts/OPNsense/Switchtracker/lib/__init__.py
opnsense/scripts/OPNsense/Switchtracker/lib/config_reader.py
opnsense/scripts/OPNsense/Switchtracker/lib/db.py
opnsense/scripts/OPNsense/Switchtracker/lib/lldp_client.py
opnsense/scripts/OPNsense/Switchtracker/lib/snmp_client.py
opnsense/scripts/OPNsense/Switchtracker/lib/vendor/__init__.py
opnsense/scripts/OPNsense/Switchtracker/lib/vendor/_base.py
opnsense/scripts/OPNsense/Switchtracker/lib/vendor/arista.py
opnsense/scripts/OPNsense/Switchtracker/lib/vendor/cisco_ios.py
opnsense/scripts/OPNsense/Switchtracker/lib/vendor/cisco_nxos.py
opnsense/scripts/OPNsense/Switchtracker/lib/vendor/juniper.py
opnsense/scripts/OPNsense/Switchtracker/poll_all.py
opnsense/scripts/OPNsense/Switchtracker/poll_lldp.py
opnsense/scripts/OPNsense/Switchtracker/poll_snmp.py
opnsense/scripts/OPNsense/Switchtracker/sql/init.sql
opnsense/service/conf/actions.d/actions_switchtracker.conf
"

echo ">>> Installing os-switchtracker..."

for FILE in ${FILES}; do
    DIR=$(dirname "${LOCALBASE}/${FILE}")
    mkdir -p "${DIR}"
    fetch -q -o "${LOCALBASE}/${FILE}" "${BASEURL}/${FILE}"
done

# Set executable permissions on Python scripts
find "${LOCALBASE}/opnsense/scripts/OPNsense/Switchtracker" -name "*.py" -exec chmod 755 {} \;

# Restart configd to pick up action definitions
echo ">>> Restarting configd..."
service configd restart

echo ">>> os-switchtracker installed successfully."
echo ""
echo "Navigate to Services > Switch Tracker in the OPNsense web UI."
echo "To uninstall, run: fetch -o - https://raw.githubusercontent.com/${REPO}/${BRANCH}/${PLUGIN_DIR}/scripts/uninstall.sh | sh"
