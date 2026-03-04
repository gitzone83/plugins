#!/usr/local/bin/python3
"""Orchestrator: runs LLDP polling, SNMP polling, offline detection, and alert checks."""

import sys
import time
from lib.db import get_connection
from lib.config_reader import read_config


def mark_offline_switches(offline_threshold):
    """Mark switches as offline if not seen within the threshold."""
    conn = get_connection()
    cutoff = time.time() - offline_threshold
    conn.execute(
        "UPDATE switches SET is_online = 0 WHERE last_seen < ? AND is_online = 1",
        (cutoff,)
    )
    conn.commit()
    conn.close()


def poll_once():
    """Run a single poll cycle."""
    config = read_config()
    general = config.get('general', {})

    if general.get('enabled', '0') != '1':
        return

    # LLDP discovery
    if general.get('lldpEnabled', '1') == '1':
        from poll_lldp import poll_lldp
        poll_lldp()

    # SNMP polling
    from poll_snmp import poll_snmp
    poll_snmp()

    # Mark offline switches
    offline_threshold = int(general.get('offlineThreshold', '900') or '900')
    mark_offline_switches(offline_threshold)

    # Check alert rules
    from check_alerts import check_alerts
    check_alerts()


if __name__ == '__main__':
    if '--once' in sys.argv:
        poll_once()
    else:
        poll_once()
