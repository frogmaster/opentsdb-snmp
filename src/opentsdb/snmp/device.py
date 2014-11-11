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
from opentsdb.snmp.metric import Metric
from opentsdb.snmp.snmp_session import SNMPSession


class Device:
    def __init__(self, data, resolvers, mods, metrics):
        self.hostname = data["hostname"]
        self.community = data["community"]
        self.snmp_version = data["snmp_version"]
        self.metrics = []
        self.resolvers = resolvers
        self.value_modifiers = mods
        for m in data["metrics"]:
            if not m in metrics:
                continue
            metric = Metric(metrics[m], self)
            self.metrics.append(metric)

    def init_snmp(self):
        self.snmp = SNMPSession(
            host=self.hostname,
            community=self.community,
            version=self.snmp_version
        )
        self.snmp.connect()
        return self.snmp

    def close_snmp(self):
        self.snmp = None

    def poll(self):
        self.init_snmp()
        if not self.snmp.session:
            return []
        data = []
        for m in self.metrics:
            data.extend(m.get_opentsdb_commands(self.snmp))
        self.close_snmp()
        return data
