import time


class Metric:
    'Metric class'
    def __init__(self, data, snmp, resolvers=None, host=None):
        self.name = data["metric"]
        self.tags = data["tags"]
        self.oid = data["oid"]
        self.host = host
        if data["type"] == "walk":
            self.walk = True
            if "resolver" in data and data["resolver"] in resolvers:
                self.resolver = resolvers[data["resolver"]]
            else:
                self.resolver = resolvers["default"]
        else:
            self.walk = False
        self.snmp = snmp

    def _get_walk(self):
        data = self.snmp.walk(self.oid)
        return data

    def _process_walk_data(self, data):
        buf = []
        for idx, dp in data.items():
            buf.append(self._process_dp(dp, idx))
        return buf

    def _process_dp(self, dp, key=None):
        tags = self.tags
        if (key):
            tags = dict(tags.items() + self.resolver().resolve(key).items())
        tags["host"] = self.host
        tagstr = self._tags_to_str(tags)
        buf = "put {0} {1} {2} {3}".format(
            self.name, int(time.time()), dp, tagstr
        )
        return buf

    def _tags_to_str(self, tagsdict):
        buf = []
        for key, val in tagsdict.items():
            buf.append(str(key) + "=" + str(val))
        if len(buf) > 0:
            return ' '.join(buf)
        else:
            return ""

    def _get_get(self):
        data = self.snmp.get(self.oid)
        return data

    def get_opentsdb_commands(self):
        if self.walk:
            raw = self._get_walk()
            return self._process_walk_data(raw)
        else:
            raw = self._get_get()
            return [self._process_dp(raw)]
