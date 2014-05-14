class Rate:
    cache = {}

    def modify(self, key, value, ts):
        new = {'ts': ts, 'value': value}
        if not key in self.cache:
            self.cache[key] = new
            return None
        old = self.cache[key]
        rate = self.rate(old['ts'], old['value'], new['ts'], new['value'])
        self.cache[key] = new
        return rate

    def rate(self, told, vold, tnew, vnew):
        rate = (vnew - vold) / (tnew - told)
        if rate >= 0:
            return rate
        w = 64
        if vold < 2 ** 32:
            w = 32
        return ((2 ** w) - vold + vnew) / (tnew - told)
