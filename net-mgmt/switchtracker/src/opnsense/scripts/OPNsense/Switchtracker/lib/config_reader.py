"""Read Switch Tracker configuration from OPNsense config.xml."""

import xml.etree.ElementTree as ET

CONFIG_PATH = '/conf/config.xml'


def read_config():
    """Parse config.xml and return switchtracker settings.

    Returns a dict with keys: general, credentials, switches, alertRules.
    """
    result = {
        'general': {},
        'credentials': [],
        'switches': [],
        'alertRules': [],
    }

    try:
        tree = ET.parse(CONFIG_PATH)
        root = tree.getroot()
    except (ET.ParseError, FileNotFoundError):
        return result

    st = root.find('.//OPNsense/switchtracker')
    if st is None:
        return result

    # General settings
    general = st.find('general')
    if general is not None:
        for child in general:
            result['general'][child.tag] = child.text or ''

    # Credentials
    creds = st.find('credentials')
    if creds is not None:
        for cred in creds.findall('credential'):
            entry = {'uuid': cred.get('uuid', '')}
            for child in cred:
                entry[child.tag] = child.text or ''
            result['credentials'].append(entry)

    # Switches
    switches = st.find('switches')
    if switches is not None:
        for sw in switches.findall('switchdev'):
            entry = {'uuid': sw.get('uuid', '')}
            for child in sw:
                entry[child.tag] = child.text or ''
            result['switches'].append(entry)

    # Alert rules
    alert_rules = st.find('alertRules')
    if alert_rules is not None:
        for rule in alert_rules.findall('alertRule'):
            entry = {'uuid': rule.get('uuid', '')}
            for child in rule:
                entry[child.tag] = child.text or ''
            result['alertRules'].append(entry)

    return result


def get_credential_by_uuid(config, uuid):
    """Look up a credential profile by UUID."""
    for cred in config.get('credentials', []):
        if cred.get('uuid') == uuid:
            return cred
    return None
