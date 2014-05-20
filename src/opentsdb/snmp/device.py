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
        self.init_snmp()
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

    def poll(self):
        data = []
        for m in self.metrics:
            data = data + m.get_opentsdb_commands()
        return data
