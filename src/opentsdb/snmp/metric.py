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
import time


class Metric:
    'Metric class'
    def __init__(self, data, device):
        self.name = data["metric"]
        self.tags = data["tags"] or {}
        self.oid = data["oid"]
        self.host = device.hostname
        self.value_modifier = None
        if data["type"] == "walk":
            self.walk = True
            if "resolver" in data and data["resolver"] in device.resolvers:
                self.resolver = device.resolvers[data["resolver"]]
            else:
                self.resolver = device.resolvers["default"]
        else:
            self.walk = False
        if "rate" in data and data["rate"]:
            self.value_modifier = device.value_modifiers["rate"]
        self.device = device

    def _get_walk(self, snmp):
        data = snmp.walk(self.oid)
        return data

    def _process_walk_data(self, data):
        buf = []
        for idx, dp in data.items():
            if dp is None:
                next
            item = self._process_dp(dp, idx)
            if (item):
                buf.append(item)
        return buf

    def _process_dp(self, dp, key=None):
        if dp is None:
            return
        tags = self.tags
        if (key):
            resolved = self.resolver.resolve(key, device=self.device)
            if resolved:
                tags = dict(
                    tags.items()
                    + resolved.items()
                )
        tagstr = self._tags_to_str(tags)
        ts = time.time()
        if self.value_modifier:
            dp = self.value_modifier.modify(
                key=self.name + tagstr,
                ts=ts,
                value=dp
            )
        if dp is None:
            return None
        buf = "put {0} {1} {2} {3}".format(
            self.name, int(ts), dp, tagstr, self.host
        )
        return buf

    def _tags_to_str(self, tagsdict):
        buf = "host=" + self.host
        for key, val in tagsdict.items():
            buf += " " + str(key) + "=" + str(val)
        return buf

    def _get_get(self, snmp):
        data = snmp.get(self.oid)
        return data

    def get_opentsdb_commands(self, snmp):
        if self.walk:
            raw = self._get_walk(snmp)
            return self._process_walk_data(raw)
        else:
            raw = self._get_get(snmp)
            return [self._process_dp(raw)]
