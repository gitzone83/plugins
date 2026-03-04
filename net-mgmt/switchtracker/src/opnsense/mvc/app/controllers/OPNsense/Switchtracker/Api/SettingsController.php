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

use OPNsense\Base\ApiMutableModelControllerBase;

class SettingsController extends ApiMutableModelControllerBase
{
    protected static $internalModelClass = '\OPNsense\Switchtracker\Switchtracker';
    protected static $internalModelName = 'switchtracker';

    /* ---- Credentials CRUD ---- */

    public function searchCredentialAction()
    {
        return $this->searchBase('credentials.credential', ['enabled', 'name', 'version', 'description']);
    }

    public function getCredentialAction($uuid = null)
    {
        return $this->getBase('credential', 'credentials.credential', $uuid);
    }

    public function addCredentialAction()
    {
        return $this->addBase('credential', 'credentials.credential');
    }

    public function setCredentialAction($uuid)
    {
        return $this->setBase('credential', 'credentials.credential', $uuid);
    }

    public function delCredentialAction($uuid)
    {
        return $this->delBase('credentials.credential', $uuid);
    }

    public function toggleCredentialAction($uuid)
    {
        return $this->toggleBase('credentials.credential', $uuid);
    }

    /* ---- Switches CRUD ---- */

    public function searchSwitchAction()
    {
        return $this->searchBase('switches.switchdev', ['enabled', 'hostname', 'address', 'snmpEnabled', 'description']);
    }

    public function getSwitchAction($uuid = null)
    {
        return $this->getBase('switchdev', 'switches.switchdev', $uuid);
    }

    public function addSwitchAction()
    {
        return $this->addBase('switchdev', 'switches.switchdev');
    }

    public function setSwitchAction($uuid)
    {
        return $this->setBase('switchdev', 'switches.switchdev', $uuid);
    }

    public function delSwitchAction($uuid)
    {
        return $this->delBase('switches.switchdev', $uuid);
    }

    public function toggleSwitchAction($uuid)
    {
        return $this->toggleBase('switches.switchdev', $uuid);
    }

    /* ---- Alert Rules CRUD ---- */

    public function searchAlertRuleAction()
    {
        return $this->searchBase('alertRules.alertRule', ['enabled', 'event', 'threshold', 'description']);
    }

    public function getAlertRuleAction($uuid = null)
    {
        return $this->getBase('alertRule', 'alertRules.alertRule', $uuid);
    }

    public function addAlertRuleAction()
    {
        return $this->addBase('alertRule', 'alertRules.alertRule');
    }

    public function setAlertRuleAction($uuid)
    {
        return $this->setBase('alertRule', 'alertRules.alertRule', $uuid);
    }

    public function delAlertRuleAction($uuid)
    {
        return $this->delBase('alertRules.alertRule', $uuid);
    }

    public function toggleAlertRuleAction($uuid)
    {
        return $this->toggleBase('alertRules.alertRule', $uuid);
    }
}
