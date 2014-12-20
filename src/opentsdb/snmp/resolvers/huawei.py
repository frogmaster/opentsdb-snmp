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
from opentsdb.snmp.resolvers.after_idx import AfterIndex


class _Huawei(object):
    def __init__(self, cache=None):
        self.cache = cache

    def index_to_name(self, index):
        bstr = "{:032b}".format(int(index))
        slot = int(bstr[15:19], 2)
        if bstr[0:7] == "1111101":
            port = int(bstr[19:24], 2)
        else:
            port = int(bstr[19:26], 2)
        return "0/{0}/{1}".format(slot, port)


class HuaweiIfName(_Huawei):
    def resolve(self, index, device=None):
        tags = {
            "index": index,
            "interface": self.index_to_name(index)
        }
        return tags


class HuaweiAfterIndex(_Huawei):
    def resolve(self, index, device=None):
        after_index = AfterIndex()
        tags = after_index.resolve(index, device=device)
        tags["interface"] = self.index_to_name(tags["index"])
        return tags


class HuaweiOnt(_Huawei):
    def resolve(self, index, device=None):
        #there may be 3 keys or 2 keys, ifindex is first, ont second
        #ontport may or may not be
        keys = index.split(".")
        idx = keys[0]
        ont = keys[1]
        gemport = self.index_to_name(idx)
        tags = {
            "interface": gemport,
            "index": index,
            "ont": ont,
        }
        if len(keys) >= 3:
            tags["ontport"] = keys[2]
        return tags
