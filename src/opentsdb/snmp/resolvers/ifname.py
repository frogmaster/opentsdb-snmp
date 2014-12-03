# This file is part of opentsdb-snmp.
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.  This program is distributed in the hope that it
# will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser
# General Public License for more details.  You should have received a copy
# of the GNU Lesser General Public License along with this program.  If not,
# see <http://www.gnu.org/licenses/>.
import logging


class IfName:
    def __init__(self, cache=None):
        self.cache = cache
        if "IfName" not in self.cache:
            self.cache["IfName"] = {}

    def get_ifnames(self, snmp):
        data = snmp.walk('.1.3.6.1.2.1.31.1.1.1.1')
        if not data:
            raise Exception("SNMP walk failed")
        return data

    def resolve(self, index, device=None):
        snmp = device.snmp
        hostname = device.hostname
        if hostname not in self.cache["IfName"]:
            self.cache["IfName"][hostname] = self.get_ifnames(snmp)
        if index in self.cache["IfName"][hostname]:
            return {"interface": self.cache["IfName"][hostname][index]}
        else:
            logging.debug("IfName Cache miss: %s %s not in %s",
                          hostname, index, hostname)
