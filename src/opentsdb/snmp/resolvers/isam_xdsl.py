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


class IsamNFXSA(object):
    def __init__(self, cache=None):
        self.cache = cache

    def resolve(self, index, device=None):
        bstr = "{:032b}".format(int(index))
        slot = int(bstr[1:7], 2)
        port = int(bstr[11:19], 2) + 1
        if slot < 10:
            slot = slot - 1
        else:
            slot = slot + 2

        interface = "1/1/{0}/{1}".format(slot, port)
        return {"interface": interface}


class IsamNFXSB(object):
    def __init__(self, cache=None):
        self.cache = cache

    def resolve(self, index, device=None):
        bstr = "{:032b}".format(int(index))
        rack = int(bstr[1:4], 2)
        shelf = int(bstr[4:6], 2)
        slot = int(bstr[6:7], 2)
        port = int(bstr[11:19], 2) + 1

        if rack <= 1:
            rack = 1
            shelf = 1
            slot = int(bstr[1:7], 2) + 2
        else:
            shelf += 1
            slot += 1

        interface = "{0}/{1}/{2}/{3}".format(rack, shelf, slot, port)
        return {"interface": interface}


class _SplitIndexVlan(object):
    def __init__(self, cache=None):
        self.cache = cache

    def resolve(self, index, device=None):
        tags = {}
        buf = ("%s" % index).split(".")
        tags["index"] = int(buf[0])
        tags["vlan"] = int(buf[1])
        return tags


class IsamNFXSAOctets(_SplitIndexVlan):
    def resolve(self, index, device=None):
        tags = super(IsamNFXSAOctets, self).resolve(index, device)
        interface_tags = IsamNFXSA().resolve(tags["index"], device)
        tags.update(interface_tags)
        return tags


class IsamNFXSBOctets(_SplitIndexVlan):
    def resolve(self, index, device=None):
        tags = super(IsamNFXSBOctets, self).resolve(index, device)
        interface_tags = IsamNFXSB().resolve(tags["index"], device)
        tags.update(interface_tags)
        return tags


class IsamOld(object):
    def __init__(self, cache=None):
        self.cache = cache

    def resolve(self, index, device=None):
        hstr = "{:x}".format(int(index))

        rack = int(hstr[0:1], 16)
        shelf = int(hstr[1:2], 16)
        slot = int(hstr[2:4], 16) + 1
        port = int(hstr[6:8], 16) + 1

        interface = "{0}/{1}/{2}/{3}".format(rack, shelf, slot, port)
        return {"interface": interface}
