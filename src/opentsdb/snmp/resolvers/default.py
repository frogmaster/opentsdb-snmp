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
class Default:
    def resolve(self, index, device=None):
        tags = {}
        buf = ("%s" % index).split(".")
        cnt = 0
        for i in buf:
            if cnt == 0:
                tags["index"] = int(i)
                cnt += 1
            else:
                cnt += 1
                tags["index%d" % cnt] = int(i)
        return tags
