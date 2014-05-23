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


class Rate:
    cache = {}

    def modify(self, key, value, ts):
        new = {'ts': ts, 'value': float(value)}
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
