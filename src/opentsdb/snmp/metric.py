import time

class Metric:
    'Metric class'
    def __init__(self, data, snmp, resolvers=None, host=None):
        self.name = data["metric"]
        self.tags = data["tags"]
        self.oid = data["oid"]
        self.host = host
        if data["resolver"] and resolvers.has_key(data["resolver"]):
            self.resolver = resolvers[data["resolver"]]
        else:
            self.resolver = resolvers["default"]
        self.snmp = snmp
        if data["type"] == "walk":
            self.walk = True

    def _get_walk(self):
        data = self.snmp.walk(oid)
        return data

    def _process_walk_data(self, data):
        buf = []
        for idx, dp in data.items():
            buf.push(self._process_dp(dp, idx))
        return buf

    def _process_dp(self, dp, key=None):
        tags = self.tags
        if (key):
            tags = tags + self.resolver(key)
        tags["host"] = self.host
        buf = "put "+self.name+" "+time.time()+" "+dp+self._tags_to_str(tags)

    def _tags_to_str(self, tagsdict):
        buf = []
        for key, val in tagsdict.items():
            buf.push(key+"="+val)
        if len(buf) > 0:
            return " "+buf.join(" ")
        else:
            return""

    def _get_get(self):
        data = self.snmp.get(oid)
        return data

    def get_opentsdb_commands(self):
        if self.walk:
            NotImplemented
