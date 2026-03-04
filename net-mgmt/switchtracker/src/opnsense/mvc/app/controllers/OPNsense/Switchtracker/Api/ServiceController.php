<?php

/*
 * Copyright (C) 2026 gitzon83 <gitzone83@gmail.com>
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 * 1. Redistributions of source code must retain the above copyright notice,
 *    this list of conditions and the following disclaimer.
 *
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in the
 *    documentation and/or other materials provided with the distribution.
 *
 * THIS SOFTWARE IS PROVIDED ``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES,
 * INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY
 * AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
 * AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
 * OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 */

namespace OPNsense\Switchtracker\Api;

use OPNsense\Base\ApiMutableServiceControllerBase;
use OPNsense\Core\Backend;

class ServiceController extends ApiMutableServiceControllerBase
{
    protected static $internalServiceClass = '\OPNsense\Switchtracker\Switchtracker';
    protected static $internalServiceEnabled = 'general.enabled';
    protected static $internalServiceName = 'switchtracker';

    /**
     * Trigger an immediate poll of all switches
     * @return array
     */
    public function pollAction()
    {
        if ($this->request->isPost()) {
            $backend = new Backend();
            $response = $backend->configdRun("switchtracker poll");
            return array("response" => $response);
        }
        return array("response" => array());
    }

    /**
     * Retrieve discovered switch inventory from SQLite
     * @return array
     */
    public function switchesAction()
    {
        $backend = new Backend();
        $response = $backend->configdRun("switchtracker dump-switches");
        $data = json_decode(trim($response), true);
        if (!is_array($data)) {
            $data = array();
        }
        return $data;
    }

    /**
     * Retrieve port status for a specific switch
     * @param string $switchId
     * @return array
     */
    public function portsAction($switchId = null)
    {
        $backend = new Backend();
        $response = $backend->configdpRun("switchtracker dump-ports", array($switchId));
        $data = json_decode(trim($response), true);
        if (!is_array($data)) {
            $data = array();
        }
        return $data;
    }

    /**
     * Retrieve topology data (nodes + edges) for D3.js visualization
     * @return array
     */
    public function topologyAction()
    {
        $backend = new Backend();
        $response = $backend->configdRun("switchtracker dump-topology");
        $data = json_decode(trim($response), true);
        if (!is_array($data)) {
            $data = array("nodes" => array(), "edges" => array());
        }
        return $data;
    }

    /**
     * Retrieve alert log entries
     * @return array
     */
    public function alertsAction()
    {
        $backend = new Backend();
        $response = $backend->configdRun("switchtracker dump-alerts");
        $data = json_decode(trim($response), true);
        if (!is_array($data)) {
            $data = array();
        }
        return $data;
    }
}
