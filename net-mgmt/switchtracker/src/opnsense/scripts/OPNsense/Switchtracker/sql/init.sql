CREATE TABLE IF NOT EXISTS switches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chassis_id TEXT UNIQUE NOT NULL,
    hostname TEXT,
    mgmt_ip TEXT,
    mac_address TEXT,
    model TEXT,
    firmware_version TEXT,
    source TEXT DEFAULT 'lldp',
    config_uuid TEXT,
    first_seen REAL NOT NULL,
    last_seen REAL NOT NULL,
    is_online INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS ports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    switch_id INTEGER NOT NULL REFERENCES switches(id) ON DELETE CASCADE,
    port_index INTEGER NOT NULL,
    port_name TEXT,
    admin_status TEXT,
    oper_status TEXT,
    speed_mbps INTEGER,
    duplex TEXT,
    vlan_id INTEGER,
    vlan_name TEXT,
    lldp_neighbor_name TEXT,
    lldp_neighbor_port TEXT,
    in_octets INTEGER DEFAULT 0,
    out_octets INTEGER DEFAULT 0,
    in_errors INTEGER DEFAULT 0,
    out_errors INTEGER DEFAULT 0,
    last_updated REAL,
    UNIQUE(switch_id, port_index)
);

CREATE TABLE IF NOT EXISTS links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    local_switch_id INTEGER NOT NULL REFERENCES switches(id) ON DELETE CASCADE,
    local_port TEXT,
    remote_chassis_id TEXT,
    remote_port TEXT,
    remote_switch_id INTEGER REFERENCES switches(id),
    first_seen REAL NOT NULL,
    last_seen REAL NOT NULL,
    UNIQUE(local_switch_id, local_port, remote_chassis_id)
);

CREATE TABLE IF NOT EXISTS alert_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp REAL NOT NULL,
    event_type TEXT NOT NULL,
    switch_id INTEGER REFERENCES switches(id),
    message TEXT NOT NULL,
    acknowledged INTEGER DEFAULT 0
);
