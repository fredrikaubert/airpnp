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

import ConfigParser

__all__ = [
    'config'
]


DEFAULTS = {
    "loglevel": "1",
    "interactive_web": "no",
    "interactive_web_port": "28080",
    "interface": "",
}


class Config(object):
    """Configuration class that exposes the contents of the configuration file
    through methods.

    """

    def __init__(self, network_interfaces, outip):
        self._parser = ConfigParser.SafeConfigParser(defaults=DEFAULTS)
        # If the file doesn't exist or doesn't have the proper section, we want the
        # defaults to take effect rather than getting a NoSectionError.
        self._parser.add_section("airpnp")
        self._nifs = network_interfaces
        self._outip = outip
        self._init_network_config() # default values

    def load(self, fileobj):
        """Load configuration from the given file-like object. The file must be in
        ConfigParser format."""
        self._parser.readfp(fileobj)
        self._init_network_config()

    def _init_network_config(self):
        iface = self._parser.get("airpnp", "interface")
        if not iface:
            # automatic detection
            iface = self._outip
        matches = [ni for ni in self._nifs if iface in ni.addresses.values()
                   or ni.name == iface]
        if len(matches) != 1:
            raise ValueError("Unrecognized interface option: %s" % iface)
        self._ni = matches[0]

    def loglevel(self):
        """Return the configured log level."""
        return self._parser.getint("airpnp", "loglevel")

    def interactive_web_enabled(self):
        """Return whether interactive web should be enabled or not."""
        return self._parser.getboolean("airpnp", "interactive_web")

    def interactive_web_port(self):
        """Return the port to use for interactive web."""
        return self._parser.getint("airpnp", "interactive_web_port")

    def interface_ip(self):
        """Return the IP address of the interface to use for listening services 
        and outbound connections."""
        import socket
        return self._ni.addresses[socket.AF_INET]

    def interface_name(self):
        """Return the name of the interface to use for listening services and
        outbound connections."""
        return self._ni.name

    def interface_index(self):
        """Return the index of the interface to use for listening services and
        outbound connections."""
        return self._ni.index


try:
    config
except NameError:
    import getnifs
    import upnp
    outip = upnp.get_outip(upnp.UpnpBase.SSDP_ADDR) # IP address
    config = Config(getnifs.get_network_interfaces(), outip)

