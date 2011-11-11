# -*- coding: utf-8 -*-
# Copyright (c) 2011, Per Rovegård <per@rovegard.se>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. Neither the name of the authors nor the names of its contributors
#    may be used to endorse or promote products derived from this software
#    without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import common
from zope.interface import implements
from twisted.application.service import IServiceMaker, MultiService
from twisted.python import log, usage
from twisted.plugin import IPlugin

from airpnp.config import config
from airpnp.bridge import BridgeServer


class Options(usage.Options):
    optParameters = [["configfile", "c", "~/.airpnprc", "The path to the Airpnp configuration file."]]


class MainService(MultiService):

    def __init__(self, interface, configfile, configloaded):
        MultiService.__init__(self)
        BridgeServer(interface).setServiceParent(self)
        self.cf = configfile
        self.cl = configloaded

    def startService(self):
        log.msg("Configuration file is %s, config loaded = %s" % (self.cf, self.cl))
        MultiService.startService(self)


class MyServiceMaker(object):
    implements(IServiceMaker, IPlugin)
    tapname = "airpnp"
    description = "AirPlay to UPnP bridge."
    options = Options

    def makeService(self, options):
        didload = config.load(options['configfile'])
        common.tweak_twisted()
        return MainService(config.interface(), options['configfile'], didload)


serviceMaker = MyServiceMaker()
