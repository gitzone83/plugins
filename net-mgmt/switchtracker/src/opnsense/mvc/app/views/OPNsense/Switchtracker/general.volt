{#
 # Copyright (C) 2026 gitzon83 <gitzone83@gmail.com>
 # All rights reserved.
 #
 # Redistribution and use in source and binary forms, with or without modification,
 # are permitted provided that the following conditions are met:
 #
 # 1.  Redistributions of source code must retain the above copyright notice,
 #     this list of conditions and the following disclaimer.
 #
 # 2.  Redistributions in binary form must reproduce the above copyright notice,
 #     this list of conditions and the following disclaimer in the documentation
 #     and/or other materials provided with the distribution.
 #
 # THIS SOFTWARE IS PROVIDED ``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES,
 # INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY
 # AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
 # AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
 # OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 # SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 # INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 # CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 # ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 # POSSIBILITY OF SUCH DAMAGE.
 #}

<script src="{{ cache_safe('/ui/js/opnsense_ui.js') }}"></script>

<ul class="nav nav-tabs" data-tabs="tabs" id="maintabs">
    <li class="active"><a data-toggle="tab" href="#settings">{{ lang._('Settings') }}</a></li>
    <li><a data-toggle="tab" href="#switches">{{ lang._('Switches') }}</a></li>
    <li><a data-toggle="tab" href="#credentials">{{ lang._('SNMP Credentials') }}</a></li>
    <li><a data-toggle="tab" href="#ports">{{ lang._('Port Status') }}</a></li>
    <li><a data-toggle="tab" href="#topology">{{ lang._('Topology') }}</a></li>
    <li><a data-toggle="tab" href="#alerts">{{ lang._('Alerts') }}</a></li>
</ul>

<div class="tab-content content-box">

    <!-- Settings Tab -->
    <div id="settings" class="tab-pane fade in active">
        {{ partial("layout_partials/base_form",['fields':generalForm,'id':'frm_general_settings'])}}
        <div class="col-md-12" style="padding-bottom: 1.5em;">
            <hr />
            <button class="btn btn-primary" id="saveAct" type="button"><b>{{ lang._('Save') }}</b> <i id="saveAct_progress"></i></button>
            <button class="btn btn-default" id="pollAct" type="button"><b>{{ lang._('Poll Now') }}</b> <i id="pollAct_progress"></i></button>
        </div>
    </div>

    <!-- Switches Tab -->
    <div id="switches" class="tab-pane fade in">
        <div class="col-md-12">
            <h3>{{ lang._('Configured Switches') }}</h3>
        </div>
        <table id="grid-switches" class="table table-condensed table-hover table-striped" data-editDialog="dialogEditSwitch" data-editAlert="SwitchChangeMessage">
            <thead>
                <tr>
                    <th data-column-id="uuid" data-type="string" data-identifier="true" data-visible="false">{{ lang._('ID') }}</th>
                    <th data-column-id="enabled" data-width="6em" data-type="string" data-formatter="rowtoggle">{{ lang._('Enabled') }}</th>
                    <th data-column-id="hostname" data-type="string">{{ lang._('Hostname') }}</th>
                    <th data-column-id="address" data-type="string">{{ lang._('Address') }}</th>
                    <th data-column-id="snmpEnabled" data-width="6em" data-type="string" data-formatter="rowtoggle">{{ lang._('SNMP') }}</th>
                    <th data-column-id="description" data-type="string">{{ lang._('Description') }}</th>
                    <th data-column-id="commands" data-width="7em" data-formatter="commands" data-sortable="false">{{ lang._('Commands') }}</th>
                </tr>
            </thead>
            <tbody>
            </tbody>
            <tfoot>
                <tr>
                    <td></td>
                    <td>
                        <button data-action="add" type="button" class="btn btn-xs btn-primary"><span class="fa fa-fw fa-plus"></span></button>
                        <button data-action="deleteSelected" type="button" class="btn btn-xs btn-default"><span class="fa fa-fw fa-trash-o"></span></button>
                    </td>
                </tr>
            </tfoot>
        </table>
        <div class="col-md-12">
            <hr />
            <h3>{{ lang._('Discovered Switches') }}</h3>
        </div>
        <table id="grid-discovered" class="table table-condensed table-hover table-striped">
            <thead>
                <tr>
                    <th data-column-id="hostname" data-type="string">{{ lang._('Hostname') }}</th>
                    <th data-column-id="mgmt_ip" data-type="string">{{ lang._('Mgmt IP') }}</th>
                    <th data-column-id="chassis_id" data-type="string">{{ lang._('Chassis ID') }}</th>
                    <th data-column-id="model" data-type="string">{{ lang._('Model') }}</th>
                    <th data-column-id="firmware_version" data-type="string">{{ lang._('Version') }}</th>
                    <th data-column-id="vendor" data-type="string">{{ lang._('Vendor') }}</th>
                    <th data-column-id="is_online" data-width="6em" data-type="string">{{ lang._('Status') }}</th>
                    <th data-column-id="last_seen" data-type="string">{{ lang._('Last Seen') }}</th>
                </tr>
            </thead>
            <tbody>
            </tbody>
        </table>
    </div>

    <!-- SNMP Credentials Tab -->
    <div id="credentials" class="tab-pane fade in">
        <table id="grid-credentials" class="table table-condensed table-hover table-striped" data-editDialog="dialogEditCredential" data-editAlert="CredentialChangeMessage">
            <thead>
                <tr>
                    <th data-column-id="uuid" data-type="string" data-identifier="true" data-visible="false">{{ lang._('ID') }}</th>
                    <th data-column-id="enabled" data-width="6em" data-type="string" data-formatter="rowtoggle">{{ lang._('Enabled') }}</th>
                    <th data-column-id="name" data-type="string">{{ lang._('Name') }}</th>
                    <th data-column-id="version" data-type="string">{{ lang._('Version') }}</th>
                    <th data-column-id="description" data-type="string">{{ lang._('Description') }}</th>
                    <th data-column-id="commands" data-width="7em" data-formatter="commands" data-sortable="false">{{ lang._('Commands') }}</th>
                </tr>
            </thead>
            <tbody>
            </tbody>
            <tfoot>
                <tr>
                    <td></td>
                    <td>
                        <button data-action="add" type="button" class="btn btn-xs btn-primary"><span class="fa fa-fw fa-plus"></span></button>
                        <button data-action="deleteSelected" type="button" class="btn btn-xs btn-default"><span class="fa fa-fw fa-trash-o"></span></button>
                    </td>
                </tr>
            </tfoot>
        </table>
    </div>

    <!-- Port Status Tab -->
    <div id="ports" class="tab-pane fade in">
        <div class="col-md-12" style="padding-bottom: 1em;">
            <label for="port_switch_select">{{ lang._('Select Switch:') }}</label>
            <select id="port_switch_select" class="selectpicker" data-width="300px"></select>
            <button class="btn btn-default btn-xs" id="refreshPorts" type="button"><span class="fa fa-fw fa-refresh"></span></button>
        </div>
        <table id="grid-ports" class="table table-condensed table-hover table-striped">
            <thead>
                <tr>
                    <th data-column-id="port_name" data-type="string">{{ lang._('Port') }}</th>
                    <th data-column-id="admin_status" data-type="string">{{ lang._('Admin') }}</th>
                    <th data-column-id="oper_status" data-type="string">{{ lang._('Oper') }}</th>
                    <th data-column-id="speed_mbps" data-type="string">{{ lang._('Speed') }}</th>
                    <th data-column-id="vlan_display" data-type="string">{{ lang._('VLAN') }}</th>
                    <th data-column-id="lldp_neighbor_name" data-type="string">{{ lang._('LLDP Neighbor') }}</th>
                    <th data-column-id="in_pkts" data-type="string">{{ lang._('In Pkts') }}</th>
                    <th data-column-id="out_pkts" data-type="string">{{ lang._('Out Pkts') }}</th>
                    <th data-column-id="in_octets" data-type="string">{{ lang._('In Bytes') }}</th>
                    <th data-column-id="out_octets" data-type="string">{{ lang._('Out Bytes') }}</th>
                    <th data-column-id="in_errors" data-type="string">{{ lang._('In Errors') }}</th>
                    <th data-column-id="out_errors" data-type="string">{{ lang._('Out Errors') }}</th>
                </tr>
            </thead>
            <tbody>
            </tbody>
        </table>
    </div>

    <!-- Topology Tab -->
    <div id="topology" class="tab-pane fade in">
        <div class="col-md-12" style="padding-bottom: 1em;">
            <button class="btn btn-default btn-xs" id="refreshTopology" type="button"><span class="fa fa-fw fa-refresh"></span> {{ lang._('Refresh') }}</button>
        </div>
        <div id="topology-graph" style="width:100%; height:600px; border:1px solid #ddd;"></div>
    </div>

    <!-- Alerts Tab -->
    <div id="alerts" class="tab-pane fade in">
        <div class="col-md-12">
            <h3>{{ lang._('Alert Rules') }}</h3>
        </div>
        <table id="grid-alertrules" class="table table-condensed table-hover table-striped" data-editDialog="dialogEditAlertRule" data-editAlert="AlertRuleChangeMessage">
            <thead>
                <tr>
                    <th data-column-id="uuid" data-type="string" data-identifier="true" data-visible="false">{{ lang._('ID') }}</th>
                    <th data-column-id="enabled" data-width="6em" data-type="string" data-formatter="rowtoggle">{{ lang._('Enabled') }}</th>
                    <th data-column-id="event" data-type="string">{{ lang._('Event') }}</th>
                    <th data-column-id="threshold" data-type="string">{{ lang._('Threshold') }}</th>
                    <th data-column-id="description" data-type="string">{{ lang._('Description') }}</th>
                    <th data-column-id="commands" data-width="7em" data-formatter="commands" data-sortable="false">{{ lang._('Commands') }}</th>
                </tr>
            </thead>
            <tbody>
            </tbody>
            <tfoot>
                <tr>
                    <td></td>
                    <td>
                        <button data-action="add" type="button" class="btn btn-xs btn-primary"><span class="fa fa-fw fa-plus"></span></button>
                        <button data-action="deleteSelected" type="button" class="btn btn-xs btn-default"><span class="fa fa-fw fa-trash-o"></span></button>
                    </td>
                </tr>
            </tfoot>
        </table>
        <div class="col-md-12">
            <hr />
            <h3>{{ lang._('Alert Log') }}</h3>
        </div>
        <table id="grid-alertlog" class="table table-condensed table-hover table-striped">
            <thead>
                <tr>
                    <th data-column-id="timestamp" data-type="string">{{ lang._('Time') }}</th>
                    <th data-column-id="event_type" data-type="string">{{ lang._('Event') }}</th>
                    <th data-column-id="message" data-type="string">{{ lang._('Message') }}</th>
                    <th data-column-id="acknowledged" data-width="6em" data-type="string">{{ lang._('Ack') }}</th>
                </tr>
            </thead>
            <tbody>
            </tbody>
        </table>
    </div>

</div>

<!-- Dialogs -->
{{ partial("layout_partials/base_dialog",['fields':formDialogEditCredential,'id':'dialogEditCredential','label':lang._('Edit SNMP Credential')])}}
{{ partial("layout_partials/base_dialog",['fields':formDialogEditSwitch,'id':'dialogEditSwitch','label':lang._('Edit Switch')])}}
{{ partial("layout_partials/base_dialog",['fields':formDialogEditAlertRule,'id':'dialogEditAlertRule','label':lang._('Edit Alert Rule')])}}

<script>
$( document ).ready(function () {
    var data_get_map = {'frm_general_settings':"/api/switchtracker/settings/get"};
    mapDataToFormUI(data_get_map).done(function(data){
        formatTokenizersUI();
        $('.selectpicker').selectpicker('refresh');
    });

    // Save general settings
    $("#saveAct").click(function () {
        saveFormToEndpoint(url="/api/switchtracker/settings/set", formid='frm_general_settings', callback_ok=function () {
            $("#saveAct_progress").addClass("fa fa-spinner fa-pulse");
            ajaxCall(url="/api/switchtracker/service/reconfigure", sendData={}, callback=function(data,status) {
                $("#saveAct_progress").removeClass("fa fa-spinner fa-pulse");
            });
        });
    });

    // Poll now button
    $("#pollAct").click(function () {
        $("#pollAct_progress").addClass("fa fa-spinner fa-pulse");
        ajaxCall(url="/api/switchtracker/service/poll", sendData={}, callback=function(data,status) {
            $("#pollAct_progress").removeClass("fa fa-spinner fa-pulse");
        });
    });

    // Credentials CRUD grid
    $("#grid-credentials").UIBootgrid({
        search:'/api/switchtracker/settings/searchCredential',
        get:'/api/switchtracker/settings/getCredential/',
        set:'/api/switchtracker/settings/setCredential/',
        add:'/api/switchtracker/settings/addCredential/',
        del:'/api/switchtracker/settings/delCredential/',
        toggle:'/api/switchtracker/settings/toggleCredential/'
    });

    // Switches CRUD grid
    $("#grid-switches").UIBootgrid({
        search:'/api/switchtracker/settings/searchSwitch',
        get:'/api/switchtracker/settings/getSwitch/',
        set:'/api/switchtracker/settings/setSwitch/',
        add:'/api/switchtracker/settings/addSwitch/',
        del:'/api/switchtracker/settings/delSwitch/',
        toggle:'/api/switchtracker/settings/toggleSwitch/'
    });

    // Alert Rules CRUD grid
    $("#grid-alertrules").UIBootgrid({
        search:'/api/switchtracker/settings/searchAlertRule',
        get:'/api/switchtracker/settings/getAlertRule/',
        set:'/api/switchtracker/settings/setAlertRule/',
        add:'/api/switchtracker/settings/addAlertRule/',
        del:'/api/switchtracker/settings/delAlertRule/',
        toggle:'/api/switchtracker/settings/toggleAlertRule/'
    });

    // Discovered switches grid (read-only, loaded from backend)
    function loadDiscoveredSwitches() {
        ajaxGet(url="/api/switchtracker/service/switches", sendData={}, callback=function(data, status) {
            var rows = data.rows || [];
            var $tbody = $("#grid-discovered tbody");
            $tbody.empty();
            $.each(rows, function(idx, sw) {
                var statusLabel = sw.is_online == 1 ?
                    '<span class="label label-success">Online</span>' :
                    '<span class="label label-danger">Offline</span>';
                $tbody.append(
                    '<tr>' +
                    '<td>' + (sw.hostname || '') + '</td>' +
                    '<td>' + (sw.mgmt_ip || '') + '</td>' +
                    '<td>' + (sw.chassis_id || '') + '</td>' +
                    '<td>' + (sw.model || '') + '</td>' +
                    '<td>' + (sw.firmware_version || '') + '</td>' +
                    '<td>' + (sw.vendor || '') + '</td>' +
                    '<td>' + statusLabel + '</td>' +
                    '<td>' + (sw.last_seen || '') + '</td>' +
                    '</tr>'
                );
            });
        });
    }

    // Load discovered switches when tab is shown
    $('a[href="#switches"]').on('shown.bs.tab', function () {
        loadDiscoveredSwitches();
    });

    // Port status tab
    function loadPortSwitchList() {
        ajaxGet(url="/api/switchtracker/service/switches", sendData={}, callback=function(data, status) {
            var rows = data.rows || [];
            var $select = $("#port_switch_select");
            $select.empty();
            $select.append('<option value="">-- Select --</option>');
            $.each(rows, function(idx, sw) {
                $select.append('<option value="' + sw.id + '">' + (sw.hostname || sw.mgmt_ip || sw.chassis_id) + '</option>');
            });
            $select.selectpicker('refresh');
        });
    }

    function loadPorts(switchId) {
        if (!switchId) return;
        ajaxGet(url="/api/switchtracker/service/ports/" + switchId, sendData={}, callback=function(data, status) {
            var rows = data.rows || [];
            var $tbody = $("#grid-ports tbody");
            $tbody.empty();
            $.each(rows, function(idx, port) {
                $tbody.append(
                    '<tr>' +
                    '<td>' + (port.port_name || port.port_index || '') + '</td>' +
                    '<td>' + (port.admin_status || '') + '</td>' +
                    '<td>' + (port.oper_status || '') + '</td>' +
                    '<td>' + (port.speed_mbps || '') + '</td>' +
                    '<td>' + (port.vlan_display || '') + '</td>' +
                    '<td>' + (port.lldp_neighbor_name || '') + '</td>' +
                    '<td>' + (port.in_pkts || '0') + '</td>' +
                    '<td>' + (port.out_pkts || '0') + '</td>' +
                    '<td>' + (port.in_octets || '0') + '</td>' +
                    '<td>' + (port.out_octets || '0') + '</td>' +
                    '<td>' + (port.in_errors || '0') + '</td>' +
                    '<td>' + (port.out_errors || '0') + '</td>' +
                    '</tr>'
                );
            });
        });
    }

    $('a[href="#ports"]').on('shown.bs.tab', function () {
        loadPortSwitchList();
    });

    $("#port_switch_select").on('change', function() {
        loadPorts($(this).val());
    });

    $("#refreshPorts").click(function() {
        loadPorts($("#port_switch_select").val());
    });

    // Alert log (read-only)
    function loadAlertLog() {
        ajaxGet(url="/api/switchtracker/service/alerts", sendData={}, callback=function(data, status) {
            var rows = data.rows || [];
            var $tbody = $("#grid-alertlog tbody");
            $tbody.empty();
            $.each(rows, function(idx, alert) {
                var ackLabel = alert.acknowledged == 1 ?
                    '<span class="label label-success">Yes</span>' :
                    '<span class="label label-default">No</span>';
                $tbody.append(
                    '<tr>' +
                    '<td>' + (alert.timestamp || '') + '</td>' +
                    '<td>' + (alert.event_type || '') + '</td>' +
                    '<td>' + (alert.message || '') + '</td>' +
                    '<td>' + ackLabel + '</td>' +
                    '</tr>'
                );
            });
        });
    }

    $('a[href="#alerts"]').on('shown.bs.tab', function () {
        loadAlertLog();
    });

    // Topology graph (pure SVG, no external libs)
    var topoSim = null;

    function loadTopology() {
        ajaxGet(url="/api/switchtracker/service/topology", sendData={}, callback=function(data, status) {
            var nodes = data.nodes || [];
            var edges = data.edges || [];
            if (!nodes.length) return;
            renderTopology(nodes, edges);
        });
    }

    function renderTopology(nodes, edges) {
        var container = document.getElementById('topology-graph');
        container.innerHTML = '';
        var W = container.clientWidth || 800;
        var H = container.clientHeight || 600;

        var ns = 'http://www.w3.org/2000/svg';
        var svg = document.createElementNS(ns, 'svg');
        svg.setAttribute('width', W);
        svg.setAttribute('height', H);
        svg.style.fontFamily = '"Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif';
        container.appendChild(svg);

        // Build id->index map
        var idMap = {};
        nodes.forEach(function(n, i) {
            idMap[n.id] = i;
            n.x = W / 2 + (Math.random() - 0.5) * W * 0.5;
            n.y = H / 2 + (Math.random() - 0.5) * H * 0.5;
            n.vx = 0;
            n.vy = 0;
        });

        // Resolve edge indices
        var links = [];
        edges.forEach(function(e) {
            var si = idMap[e.source], ti = idMap[e.target];
            if (si !== undefined && ti !== undefined) {
                links.push({
                    source: si, target: ti,
                    sourcePort: e.sourcePort || '', targetPort: e.targetPort || ''
                });
            }
        });

        // SVG elements - edges first (behind nodes)
        var edgeEls = [];
        var edgeLabelEls = [];
        links.forEach(function(l) {
            var line = document.createElementNS(ns, 'line');
            line.setAttribute('stroke', '#999');
            line.setAttribute('stroke-width', 2);
            svg.appendChild(line);
            edgeEls.push(line);
            var label = document.createElementNS(ns, 'text');
            label.setAttribute('font-size', '10');
            label.setAttribute('fill', '#666');
            label.setAttribute('text-anchor', 'middle');
            svg.appendChild(label);
            edgeLabelEls.push(label);
        });

        // Node groups
        var nodeR = 24;
        var nodeEls = [];
        nodes.forEach(function(n, i) {
            var g = document.createElementNS(ns, 'g');
            g.style.cursor = 'grab';

            var circle = document.createElementNS(ns, 'circle');
            circle.setAttribute('r', nodeR);
            circle.setAttribute('fill', n.local ? '#d9534f' : (n.online ? '#5cb85c' : '#aaa'));
            circle.setAttribute('stroke', '#fff');
            circle.setAttribute('stroke-width', 2);
            g.appendChild(circle);

            // Icon text (switch or firewall)
            var icon = document.createElementNS(ns, 'text');
            icon.setAttribute('text-anchor', 'middle');
            icon.setAttribute('dy', '5');
            icon.setAttribute('fill', '#fff');
            icon.setAttribute('font-size', '16');
            icon.setAttribute('font-weight', 'bold');
            icon.textContent = n.local ? '\u2691' : '\u2630';
            g.appendChild(icon);

            // Label below
            var label = document.createElementNS(ns, 'text');
            label.setAttribute('text-anchor', 'middle');
            label.setAttribute('dy', nodeR + 14);
            label.setAttribute('font-size', '12');
            label.setAttribute('font-weight', '600');
            label.setAttribute('fill', '#333');
            label.textContent = n.label;
            g.appendChild(label);

            // IP below label
            if (n.ip) {
                var ipLabel = document.createElementNS(ns, 'text');
                ipLabel.setAttribute('text-anchor', 'middle');
                ipLabel.setAttribute('dy', nodeR + 27);
                ipLabel.setAttribute('font-size', '10');
                ipLabel.setAttribute('fill', '#888');
                ipLabel.textContent = n.ip;
                g.appendChild(ipLabel);
            }

            svg.appendChild(g);
            nodeEls.push(g);

            // Drag behavior
            (function(idx) {
                var dragging = false, ox, oy;
                g.addEventListener('mousedown', function(e) {
                    dragging = true;
                    ox = e.clientX - nodes[idx].x;
                    oy = e.clientY - nodes[idx].y;
                    nodes[idx].fixed = true;
                    g.style.cursor = 'grabbing';
                    e.preventDefault();
                });
                document.addEventListener('mousemove', function(e) {
                    if (!dragging) return;
                    nodes[idx].x = e.clientX - ox;
                    nodes[idx].y = e.clientY - oy;
                    nodes[idx].vx = 0;
                    nodes[idx].vy = 0;
                    tick();
                });
                document.addEventListener('mouseup', function() {
                    if (dragging) {
                        dragging = false;
                        nodes[idx].fixed = false;
                        g.style.cursor = 'grab';
                    }
                });
            })(i);
        });

        function tick() {
            nodeEls.forEach(function(g, i) {
                g.setAttribute('transform', 'translate(' + nodes[i].x + ',' + nodes[i].y + ')');
            });
            edgeEls.forEach(function(line, i) {
                var s = nodes[links[i].source], t = nodes[links[i].target];
                line.setAttribute('x1', s.x);
                line.setAttribute('y1', s.y);
                line.setAttribute('x2', t.x);
                line.setAttribute('y2', t.y);
            });
            edgeLabelEls.forEach(function(lbl, i) {
                var s = nodes[links[i].source], t = nodes[links[i].target];
                lbl.setAttribute('x', (s.x + t.x) / 2);
                lbl.setAttribute('y', (s.y + t.y) / 2 - 5);
                var parts = [];
                if (links[i].sourcePort) parts.push(links[i].sourcePort);
                if (links[i].targetPort) parts.push(links[i].targetPort);
                lbl.textContent = parts.join(' \u2194 ');
            });
        }

        // Simple force simulation
        var alpha = 1.0;
        var springLen = 180;
        var repulsion = 3000;
        var damping = 0.85;

        function simulate() {
            if (alpha < 0.001) { topoSim = null; return; }
            alpha *= 0.99;

            // Repulsion between all node pairs
            for (var i = 0; i < nodes.length; i++) {
                for (var j = i + 1; j < nodes.length; j++) {
                    var dx = nodes[j].x - nodes[i].x;
                    var dy = nodes[j].y - nodes[i].y;
                    var dist = Math.sqrt(dx * dx + dy * dy) || 1;
                    var force = repulsion / (dist * dist);
                    var fx = dx / dist * force * alpha;
                    var fy = dy / dist * force * alpha;
                    if (!nodes[i].fixed) { nodes[i].vx -= fx; nodes[i].vy -= fy; }
                    if (!nodes[j].fixed) { nodes[j].vx += fx; nodes[j].vy += fy; }
                }
            }

            // Spring attraction along edges
            links.forEach(function(l) {
                var s = nodes[l.source], t = nodes[l.target];
                var dx = t.x - s.x, dy = t.y - s.y;
                var dist = Math.sqrt(dx * dx + dy * dy) || 1;
                var force = (dist - springLen) * 0.05 * alpha;
                var fx = dx / dist * force;
                var fy = dy / dist * force;
                if (!s.fixed) { s.vx += fx; s.vy += fy; }
                if (!t.fixed) { t.vx -= fx; t.vy -= fy; }
            });

            // Center gravity
            nodes.forEach(function(n) {
                if (n.fixed) return;
                n.vx += (W / 2 - n.x) * 0.01 * alpha;
                n.vy += (H / 2 - n.y) * 0.01 * alpha;
            });

            // Apply velocity
            nodes.forEach(function(n) {
                if (n.fixed) return;
                n.vx *= damping;
                n.vy *= damping;
                n.x += n.vx;
                n.y += n.vy;
                // Keep in bounds
                n.x = Math.max(nodeR + 5, Math.min(W - nodeR - 5, n.x));
                n.y = Math.max(nodeR + 5, Math.min(H - nodeR - 30, n.y));
            });

            tick();
            topoSim = requestAnimationFrame(simulate);
        }

        tick();
        topoSim = requestAnimationFrame(simulate);
    }

    $('a[href="#topology"]').on('shown.bs.tab', function () {
        loadTopology();
    });

    $("#refreshTopology").click(function() {
        if (topoSim) { cancelAnimationFrame(topoSim); topoSim = null; }
        loadTopology();
    });
});
</script>
