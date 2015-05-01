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


class NECIPasoModem:
    def __init__(self, cache=None):
        self.cache = cache
        self._map = {
            16842752: "modem1",
            25231360: "modem2",
        }

    def resolve(self, index, device=None):
        if (int(index) in self._map):
            interface =  self._map[int(index)]
            return {"interface": interface}
        raise Exception("Missing INDEX {} in NECIPasoModem resolver".format(index))
