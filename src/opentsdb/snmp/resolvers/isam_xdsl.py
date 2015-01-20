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
import logging


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


class Dot1dBasePortIfIndex(object):
    def __init__(self, cache=None):
        self.cache = cache
        if "ISAMOCTETS" not in self.cache:
            self.cache["ISAMOCTETS"] = dict()

    def get_dot1dbaseport(self, snmp):
        data = snmp.walk('.1.3.6.1.2.1.17.1.4.1.2')
        if not data:
            raise Exception("SNMP walk failed")
        return data

    def get_atmVCLMapAtmIfIndex(self, snmp):
        data = snmp.walk('.1.3.6.1.4.1.637.61.1.4.1.73.1.1')
        if not data:
            raise Exception("SNMP walk failed")
        return data

    def get_map(self, snmp):
        dot1d = self.get_dot1dbaseport(snmp)
        atm = self.get_atmVCLMapAtmIfIndex(snmp)
        ret = dict()

        for key, val in dot1d.iteritems():
            val = "{0}".format(val)
            if val in atm:
                ret[key] = atm[val]
            else:
                ret[key] = -1
        return ret

    def resolve(self, baseport, device=None):
        snmp = device.snmp
        name = "ISAMOCTETS"
        hostname = device.hostname
        c_key = name + "_" + hostname
        if c_key not in self.cache:
            self.cache[c_key] = self.get_map(snmp)

        baseport = str(baseport)
        if baseport in self.cache[c_key]:
            if self.cache[c_key][baseport] is not -1:
                return {"index": self.cache[c_key][baseport]}
            else:
                logging.debug("Non atm interface, don't care")
                return None
        else:
            #baseport is dynamic, maybe it's been added, re-init the cache
            self.cache[c_key] = self.get_map(snmp)
            if baseport in self.cache[c_key]:
                if self.cache[c_key][baseport] is not -1:
                    return {"index": self.cache[c_key][baseport]}
                else:
                    logging.debug("Non atm interface, don't care")
                    return None
            else:
                logging.debug("Cache miss: %s %s not in %s",
                              hostname, baseport, hostname)


class IsamOldOctets(Dot1dBasePortIfIndex):
    def resolve(self, index, device=None):
        tags = _SplitIndexVlan().resolve(index, device=device)
        new_tags = super(IsamOldOctets, self).resolve(tags["index"], device)
        if not new_tags:
            return None
        tags.update(new_tags)
        interface_tags = IsamOld().resolve(tags["index"], device)
        tags.update(interface_tags)
        return tags
