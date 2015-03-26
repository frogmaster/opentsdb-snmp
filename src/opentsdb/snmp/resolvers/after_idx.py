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


class AfterIndex:
    def __init__(self, cache=None):
        self.cache = cache

    def resolve(self, index, device=None, updown=False, reverse=False):
        tags = {}
        buf = ("%s" % index).split(".")
        tags["index"] = int(buf[0])
        if int(buf[1]) == 2 or (int(buf[1]) == 1 and reverse):
            tags["direction"] = "us" if updown else "out"
        elif int(buf[1]) == 1 or (int(buf[1]) == 2 and reverse):
            tags["direction"] = "ds" if updown else "in"
        else:
            raise Exception("Direction after Index Resolve failed")
        return tags
