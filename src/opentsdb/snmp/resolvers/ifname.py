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
class IfName:
    cache = {}

    def _init_cache(self):
        if self.hostname not in IfName.cache:
            ifnames = self.get_ifnames()
            IfName.cache[self.hostname] = ifnames

    def get_ifnames(self):
        data = self.snmp_session.walk('.1.3.6.1.2.1.31.1.1.1.1')
        if not data:
            raise Exception("SNMP walk failed")
        return data

    def resolve(self, index, device=None):
        self.snmp_session = device.snmp
        self.hostname = device.hostname
        self._init_cache()
        return IfName.cache[self.hostname][index]
