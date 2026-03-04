#!/usr/local/bin/python3
"""Check alert rules against current state and emit syslog / dump alert log."""

import json
import sys
import syslog
import time
from lib.db import get_connection, dict_from_row
from lib.config_reader import read_config


def check_alerts():
    """Evaluate alert rules against SQLite state, log events."""
    config = read_config()
    alert_rules = config.get('alertRules', [])
    if not alert_rules:
        return

    conn = get_connection()
    now = time.time()

    for rule in alert_rules:
        if rule.get('enabled', '0') != '1':
            continue

        event = rule.get('event', '')

        if event == 'switch_offline':
            offline_switches = conn.execute(
                "SELECT id, hostname, chassis_id FROM switches WHERE is_online = 0"
            ).fetchall()
            for sw in offline_switches:
                sw_dict = dict_from_row(sw)
                msg = "Switch offline: %s (%s)" % (sw_dict['hostname'], sw_dict['chassis_id'])
                _log_alert(conn, now, event, sw_dict['id'], msg)

        elif event == 'switch_new':
            # New switches seen in the last polling interval (5 min default)
            threshold_time = now - 300
            new_switches = conn.execute(
                "SELECT id, hostname, chassis_id FROM switches WHERE first_seen > ?",
                (threshold_time,)
            ).fetchall()
            for sw in new_switches:
                sw_dict = dict_from_row(sw)
                msg = "New switch discovered: %s (%s)" % (sw_dict['hostname'], sw_dict['chassis_id'])
                _log_alert(conn, now, event, sw_dict['id'], msg)

        elif event == 'port_down':
            down_ports = conn.execute(
                """SELECT p.switch_id, p.port_name, s.hostname
                   FROM ports p JOIN switches s ON p.switch_id = s.id
                   WHERE p.oper_status = 'down' AND p.admin_status = 'up'"""
            ).fetchall()
            for port in down_ports:
                p = dict_from_row(port)
                msg = "Port down: %s on %s" % (p['port_name'], p['hostname'])
                _log_alert(conn, now, event, p['switch_id'], msg)

        elif event == 'port_errors':
            threshold = int(rule.get('threshold', '0') or '0')
            error_ports = conn.execute(
                """SELECT p.switch_id, p.port_name, p.in_errors, p.out_errors, s.hostname
                   FROM ports p JOIN switches s ON p.switch_id = s.id
                   WHERE (p.in_errors + p.out_errors) > ?""",
                (threshold,)
            ).fetchall()
            for port in error_ports:
                p = dict_from_row(port)
                total = p['in_errors'] + p['out_errors']
                msg = "Port errors on %s %s: %d total (%d in, %d out)" % (
                    p['hostname'], p['port_name'], total, p['in_errors'], p['out_errors'])
                _log_alert(conn, now, event, p['switch_id'], msg)

    conn.commit()
    conn.close()


def _log_alert(conn, timestamp, event_type, switch_id, message):
    """Insert an alert log entry and emit syslog."""
    # Avoid duplicate alerts within 5 minutes
    existing = conn.execute(
        """SELECT id FROM alert_log
           WHERE event_type = ? AND switch_id = ? AND message = ?
           AND timestamp > ?""",
        (event_type, switch_id, message, timestamp - 300)
    ).fetchone()

    if existing:
        return

    conn.execute(
        "INSERT INTO alert_log (timestamp, event_type, switch_id, message) VALUES (?, ?, ?, ?)",
        (timestamp, event_type, switch_id, message)
    )
    syslog.openlog('switchtracker', syslog.LOG_PID, syslog.LOG_LOCAL0)
    syslog.syslog(syslog.LOG_WARNING, message)
    syslog.closelog()


def dump_alerts():
    """Output alert log as JSON."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM alert_log ORDER BY timestamp DESC LIMIT 500"
    ).fetchall()
    conn.close()

    alerts = []
    for row in rows:
        alert = dict_from_row(row)
        if alert.get('timestamp'):
            alert['timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(alert['timestamp']))
        alerts.append(alert)

    print(json.dumps({'rows': alerts}))


if __name__ == '__main__':
    if '--dump' in sys.argv:
        dump_alerts()
    else:
        check_alerts()
