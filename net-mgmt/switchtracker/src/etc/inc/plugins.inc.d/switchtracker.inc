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

function switchtracker_services()
{
    global $config;

    $services = array();

    if (
        isset($config['OPNsense']['switchtracker']['general']['enabled']) &&
        $config['OPNsense']['switchtracker']['general']['enabled'] == 1
    ) {
        $services[] = array(
            'description' => gettext('Switch Tracker'),
            'configd' => array(
                'restart' => array('switchtracker poll'),
            ),
            'nocheck' => true,
            'name' => 'switchtracker',
        );
    }

    return $services;
}

function switchtracker_cron()
{
    global $config;

    $jobs = array();

    if (
        isset($config['OPNsense']['switchtracker']['general']['enabled']) &&
        $config['OPNsense']['switchtracker']['general']['enabled'] == 1
    ) {
        $interval = '5';
        if (!empty($config['OPNsense']['switchtracker']['general']['pollInterval'])) {
            $interval = (string) max(1, intval($config['OPNsense']['switchtracker']['general']['pollInterval']) / 60);
        }
        $jobs[] = array(
            'minutes' => '*/' . $interval,
            'command' => 'switchtracker poll',
            'description' => 'Switch Tracker polling',
        );
    }

    return $jobs;
}

function switchtracker_syslog()
{
    $logfacilities = array();

    $logfacilities['switchtracker'] = array(
        'facility' => array('switchtracker'),
    );

    return $logfacilities;
}
