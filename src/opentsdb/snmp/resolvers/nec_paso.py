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
        self._errtypemap = {
            2: "es",
            3: "ses",
            5: "ua",
        }

    def resolve(self, index, device=None):
        arr = str(index).split(".")
        ret = {}
        if len(arr) == 2:
            if int(arr[1]) in self._errtypemap:
                ret["type"] = self._errtypemap[int(arr[1])]
            else:
                return None
            index = arr[0]

        if (int(index) in self._map):
            ret["interface"] = self._map[int(index)]
            return ret
        raise Exception(
            "Missing INDEX {} in NECIPasoModem resolver".format(index)
        )


class NECPasoNEOModem:
    def __init__(self, cache=None):
        self.cache = cache

    def resolve(self, index, device=None):
        return {"interface": "modem{}".format(index)}
