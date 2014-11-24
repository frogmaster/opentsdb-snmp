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


class HwdslamChannel:
    def __init__(self, cache=None):
        self.cache = cache

    def resolve(self, index, device=None):
        #resolve index and direction
        #Previous code had this, guess it's neened, probably some xdsl channel
        #stuff or something...

        index = index + 33554431
        after_idx_resolver = device.resolvers["after_idx"]
        tags = after_idx_resolver.resolve(index, device=device)
        #resolve ifname
        ifnameresolver = device.resolvers["ifname"]
        ifnametags = ifnameresolver.resolve(tags["index"], device=device)
        tags.update(ifnametags)
        return tags
