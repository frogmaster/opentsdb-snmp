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
