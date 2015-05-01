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
import logging
from string import Formatter
import copy


class Metric:
    'Metric class'
    def __init__(self, device, metric=None, tags={}, oid=None, multiply=None,
                 type=None, rate=None, ignore_zeros=False, resolver="default",
                 startidx=None, endidx=None, max_val=None, min_val=None,
                 replacement_val=None, rate_rand_wraps=False):
        self.name = metric
        self.tags = copy.deepcopy(tags)
        self.oid = oid
        self.startidx = startidx
        self.endidx = endidx
        self.device = device
        self.host = device.hostname
        self.max_val = max_val
        self.min_val = min_val
        self.replacement_val = replacement_val
        self.rate_rand_wraps = rate_rand_wraps
        self.ignore_zeros = ignore_zeros

        self.tags["host"] = self.host

        if multiply:
            self.multiply = float(multiply)
        else:
            self.multiply = multiply

        if (rate):
            self.value_modifier = device.value_modifiers["rate"]
        else:
            self.value_modifier = None

        if type == "walk" or type == "bulkwalk":
            self.walk = type
            if resolver not in device.resolvers:
                raise Exception("Resolver not found")
            self.resolver = device.resolvers[resolver]
        else:
            self.walk = False

    def _get_walk(self, snmp):
        if self.walk == "bulkwalk":
            data = snmp.bulkwalk(
                self.oid,
                startidx=self.startidx,
                endidx=self.endidx
            )
        else:
            data = snmp.walk(self.oid, expect_str=False)
        return data

    def _process_walk_data(self, data, poll_time):
        buf = []
        for idx, dp in data.items():
            if dp is None:
                next
            item = self._process_dp(dp, poll_time, key=idx)
            if (item):
                buf.append(item)
        return buf

    def _process_dp(self, dp, poll_time, key=None):
        if not dp and (dp is None or self.ignore_zeros):
            return None
        tags = self.tags.copy()
        if (key):
            resolved = self.resolver.resolve(key, device=self.device)
            if resolved:
                tags.update(resolved)
            else:
                return None
        (metric, tags) = self._tags_to_metric(tags)
        tagstr = self._tags_to_str(tags)
        ts = time.time()
        if self.value_modifier:
            dp = self.value_modifier.modify(
                key=metric + tagstr,
                ts=ts,
                value=dp,
                rate_rand_wraps=self.rate_rand_wraps
            )
        if dp is None:
            return None

        if self.max_val is not None and long(dp) > long(self.max_val):
            dp = self.replacement_val
        elif self.min_val is not None and long(dp) < long(self.min_val):
            dp = self.replacement_val
        if dp is None:
            return None
        if self.multiply:
            dp = float(dp) * self.multiply
        buf = "put {0} {1} {2} {3}".format(
            metric, int(poll_time), dp, tagstr
        )
        return buf

    def _tags_to_metric(self, tags):
        """
        formats metric name and removes used items from tags
        retruns tuple (new_metric_name, tags)
        """
        f = Formatter()
        #get keys from metric name
        parsed = f.parse(self.name)
        keymap = dict()
        for tup in parsed:
            if (tup[1]):
                keymap[tup[1]] = True
        if not keymap:
            return (self.name, tags)
        #create new metric string
        metric = f.format(self.name, **tags)
        #remove used tags
        for i in keymap.keys():
            del tags[i]
        return (metric, tags)

    def _tags_to_str(self, tagsdict):
        buff_arr = []
        for key, val in tagsdict.items():
            buff_arr.append(str(key) + "=" + str(val))
        return " ".join(buff_arr)

    def _get_get(self, snmp):
        data = snmp.get(self.oid)
        return data

    def get_opentsdb_commands(self, snmp, poll_time):
        if self.walk:
            raw = self._get_walk(snmp)
            logging.debug("got metric %s from %s, variable count %s",
                          self.name, self.host, len(raw.keys()))
            return self._process_walk_data(raw, poll_time)
        else:
            raw = self._get_get(snmp)
            return [self._process_dp(raw, poll_time)]
