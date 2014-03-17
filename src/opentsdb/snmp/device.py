from opentsdb.snmp.metric import Metric
from opentsdb.snmp.snmp_session import SNMPSession

class Device:
    def __init__(self, data):
        self.hostname=data["hostname"]
        self.community=data["community"]
        self.snmp_version=data["snmp_version"]
        self.metrics = []
        self.resolvers = { "default" : default_resolver()
                }
        self.init_snmp()
        for m in data["metrics"]:
            self.metrics.append(Metric(m, self.snmp, resolvers=self.resolvers, host=self.hostname))

    def init_snmp(self):
        self.snmp = SNMPSession(host=self.hostname, community=self.community, version=self.snmp_version)

    def poll(self):
        for m in self.metrics:
            NotImplemented


class default_resolver:
    cache=None
    snmp_session=None

    def resolve(self, index):
        tags = {}
        buf = ("%s" % index).split(".")
        cnt = 0
        for i in buf:
            if cnt == 0:
                tags["index"] = i
                cnt += 1
            else:
                cnt += 1
                tags["index%d" % cnt] = i
        return tags


class IfName_resolver:
    cache=None
    snmp_session=None

    def __init__(self, snmp, cache):
        self.cache=cache
        self.snmp_session=snmp
        self._init_cache()

    def _init_cache(self):
        if not self.cache["ifName"]:
            self.cache["ifName"] = self.get_ifnames()

    def get_ifnames(self):
        data = self.snmp_session.walk('.1.3.6.1.2.1.31.1.1.1.1')
        if not data:
            return None
        return data

    def resolve(self, index):
        return self.cache["ifName"][index];
