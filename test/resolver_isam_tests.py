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
from nose.tools import eq_, raises, ok_
import opentsdb.snmp.resolvers.isam_xdsl as i
from mock import Mock


class TestISAM(object):
    def setup(self):
        self.device = Mock()
        self.device.hostname = "foobar"
        self.device.snmp = Mock()

    def test_NFXSAcard_resolver(self):
        resolver = i.NFXSAcard()
        testdata = [
            {"index": "4352",  "expected": "acu:1/1"},
            {"index": "8448",  "expected": "acu:2/1"},
            {"index": "4353",  "expected": "nt-a"},
            {"index": "4354", "expected": "nt-b"},
            {"index": "8449", "expected": "ctrl:2/1"},
            {"index": "8705", "expected": "ctrl:2/2"},
            {"index": "8961", "expected": "ctrl:2/3"},
            {"index": "9217", "expected": "ctrl:2/4"},
            {"index": "12545", "expected": "ctrl:3/1"},
            {"index": "4360", "expected": "1/1/6"},
            {"index": "4361", "expected": "1/1/7"},
            {"index": "4362", "expected": "1/1/8"},
            {"index": "4363", "expected": "1/1/12"},
            {"index": "4364", "expected": "1/1/13"},
            {"index": "4365", "expected": "1/1/14"},
            {"index": "4366", "expected": "1/1/15"},
            {"index": "9219", "expected": "2/4/1"},
            {"index": "8707", "expected": "2/2/1"},
        ]

        for item in testdata:
            tags = resolver.resolve(item["index"])
            eq_(item["expected"], tags["card"])

        tags = resolver.resolve("4360.1")
        ok_(tags["card"] == "1/1/6")
        ok_(tags["index"] == "1")

    def test_NFXSBcard_resolver(self):
        resolver = i.NFXSBcard()
        testdata = [
            {"index": "4352",  "expected": "acu:1/1"},
            {"index": "8448",  "expected": "acu:2/1"},
            {"index": "4353",  "expected": "nt-a"},
            {"index": "4354", "expected": "nt-b"},
            {"index": "8449", "expected": "ctrl:2/1"},
            {"index": "8705", "expected": "ctrl:2/2"},
            {"index": "8961", "expected": "ctrl:2/3"},
            {"index": "9217", "expected": "ctrl:2/4"},
            {"index": "4355", "expected": "1/1/4"},
            {"index": "4356", "expected": "1/1/5"},
            {"index": "4357", "expected": "1/1/6"},
            {"index": "4358", "expected": "1/1/7"},
            {"index": "4359", "expected": "1/1/8"},
            {"index": "4360", "expected": "1/1/9"},
            {"index": "4361", "expected": "1/1/10"},
            {"index": "4362", "expected": "1/1/11"},
            {"index": "4363", "expected": "1/1/12"},
            {"index": "4364", "expected": "1/1/13"},
            {"index": "4365", "expected": "1/1/14"},
            {"index": "4366", "expected": "1/1/15"},
            {"index": "4367", "expected": "1/1/16"},
            {"index": "4368", "expected": "1/1/17"},
            {"index": "4369", "expected": "1/1/18"},
            {"index": "4370", "expected": "1/1/19"},
            {"index": "4481", "expected": "1/1/130"},
            {"index": "4483", "expected": "1/1/132"},
            {"index": "4484", "expected": "1/1/133"},
            {"index": "4485", "expected": "1/1/134"},
            {"index": "4486", "expected": "1/1/135"},
        ]

        for item in testdata:
            tags = resolver.resolve(item["index"])
            eq_(item["expected"], tags["card"])

        tags = resolver.resolve("4355.1")
        ok_(tags["card"] == "1/1/4")
        ok_(tags["index"] == "1")

    def test_IsamNFXSB_resolver(self):
        resolver = i.IsamNFXSB()
        testdata = [
            {"index": "67108864",  "expected": "1/1/4/1"},
            {"index": "67125248",  "expected": "1/1/4/3"},
            {"index": "67493888",  "expected": "1/1/4/48"},
            {"index": "134217728", "expected": "1/1/6/1"},
            {"index": "134455296", "expected": "1/1/6/30"},
            {"index": "536920064", "expected": "2/1/1/7"},
            {"index": "537247744", "expected": "2/1/1/47"},
            {"index": "604028928", "expected": "2/2/1/7"},
            {"index": "671277056", "expected": "2/3/1/24"},
        ]

        for item in testdata:
            tags = resolver.resolve(item["index"])
            eq_(item["expected"], tags["interface"])

    def test_Isam56NFXSB_resolver(self):
        resolver = i.Isam56NFXSB()
        testdata = [
            {"index": "1080040960", "expected": "1/1/5/16"},
            {"index": "1077960192", "expected": "1/1/4/48"},
            {"index": "1077957120", "expected": "1/1/4/42"},
        ]

        for item in testdata:
            tags = resolver.resolve(item["index"])
            eq_(item["expected"], tags["interface"])

    def test_IsamNFXSA_resolver(self):
        resolver = i.IsamNFXSA()
        testdata = [
            {"index": "67108864",  "expected": "1/1/1/1"},
            {"index": "67231744",  "expected": "1/1/1/16"},
            {"index": "101048320", "expected": "1/1/2/48"},
            {"index": "302333952", "expected": "1/1/8/43"},
            {"index": "335929344", "expected": "1/1/12/48"},
            {"index": "570425344", "expected": "1/1/19/1"},
            {"index": "46194688",  "expected": "1/1/1/8"},
            {"index": "33554432",  "expected": "1/1/1/1"},
        ]

        for item in testdata:
            tags = resolver.resolve(item["index"])
            eq_(item["expected"], tags["interface"])

    def test_Isam56NFXSA_resolver(self):
        resolver = i.Isam56NFXSA()
        testdata = [
            {"index": "1077938176", "expected": "1/1/1/5"},
            {"index": "1080049152", "expected": "1/1/2/32"},
            {"index": "1084238848", "expected": "1/1/4/23"},
            {"index": "1086325760", "expected": "1/1/5/3"},
            {"index": "1092640256", "expected": "1/1/8/48"},
            {"index": "1098929152", "expected": "1/1/14/43"},
            {"index": "1107558400", "expected": "1/1/18/1"},
            {"index": "1094713856", "expected": "1/1/12/2"},
        ]

        for item in testdata:
            tags = resolver.resolve(item["index"])
            eq_(item["expected"], tags["interface"])

    def test_IsamNFXSBOctets_resolver(self):
        resolver = i.IsamNFXSBOctets()
        testdata = [
            {"index": "67493888.101",  "expected": "1/1/4/48"},
            {"index": "671277056.101", "expected": "2/3/1/24"},
        ]
        for item in testdata:
            tags = resolver.resolve(item["index"])
            eq_(item["expected"], tags["interface"])
            eq_(101, tags["vlan"])

    def test_Isam56NFXSBOctets_resolver(self):
        resolver = i.Isam56NFXSBOctets()
        testdata = [
            {"index": "1080835072.101", "expected": "1/1/5/31"},
            {"index": "1078723072.101", "expected": "1/1/4/2"},
        ]
        for item in testdata:
            tags = resolver.resolve(item["index"])
            eq_(item["expected"], tags["interface"])
            eq_(101, tags["vlan"])

    def test_IsamNFXSAOctets_resolver(self):
        resolver = i.IsamNFXSAOctets()
        testdata = [
            {"index": "67231744.101", "expected": "1/1/1/16"},
            {"index": "570425344.101", "expected": "1/1/19/1"},
        ]
        for item in testdata:
            tags = resolver.resolve(item["index"])
            eq_(item["expected"], tags["interface"])
            eq_(101, tags["vlan"])

    def test_Isam56NFXSAOctets_resolver(self):
        resolver = i.Isam56NFXSAOctets()
        testdata = [
            {"index": "1085028928.101", "expected": "1/1/4/30"},
            {"index": "1108082688.101", "expected": "1/1/18/1"},
        ]
        for item in testdata:
            tags = resolver.resolve(item["index"])
            eq_(item["expected"], tags["interface"])
            eq_(101, tags["vlan"])

    def test_IsamOld_resolver(self):
        resolver = i.IsamOld()
        testdata = [
            {"index": 285409282, "expected": "1/1/4/3"},
            {"index": 285474863, "expected": "1/1/5/48"},
            {"index": 285540398, "expected": "1/1/6/47"},
            {"index": 285999109, "expected": "1/1/13/6"},
            {"index": 286195759, "expected": "1/1/16/48"},
            {"index": 286392343, "expected": "1/1/19/24"},
        ]

        for item in testdata:
            tags = resolver.resolve(item["index"])
            eq_(item["expected"], tags["interface"])

    def test_IsamOldOctets_resolver(self):
        r = i.IsamOldOctets(dict())

        def walk_side_effect(arg):
            if (arg == ".1.3.6.1.2.1.17.1.4.1.2"):
                return {"417": 136314880, "418": 136314912}
            else:
                return {"136314880": 285421568, "136314912": 285421568}

        self.device.snmp.walk = Mock()
        self.device.snmp.walk.side_effect = walk_side_effect
        tags = r.resolve("417.1500", self.device)

        eq_('1/1/4/1', tags["interface"])

    def test_IsamOldOctets_resolver_cached(self):
        r = i.IsamOldOctets(dict())

        def walk_side_effect(arg):
            if (arg == ".1.3.6.1.2.1.17.1.4.1.2"):
                return {"417": 136314880, "418": 136314912}
            else:
                return {"136314880": 285421568, "136314912": 285421568}

        self.device.snmp.walk = Mock()
        self.device.snmp.walk.side_effect = walk_side_effect

        r.resolve("417.1500", self.device)

        def walk_side_effect(arg):
            if (arg == ".1.3.6.1.2.1.17.1.4.1.2"):
                return None
            else:
                return {"136314880": 285421568, "136314912": 285421568}

        #shold still work, because of cache
        self.device.snmp.walk.side_effect = walk_side_effect
        tags = r.resolve("417.1500", self.device)
        eq_('1/1/4/1', tags["interface"])

    @raises(Exception)
    def test_IsamOldOctets_resolver_cached_failed(self):
        r = i.IsamOldOctets(dict())

        def walk_side_effect(arg):
            if (arg == ".1.3.6.1.2.1.17.1.4.1.2"):
                return {"417": 136314880, "418": 136314912}
            else:
                return {"136314880": 285421568, "136314912": 285421568}

        self.device.snmp.walk = Mock()
        self.device.snmp.walk.side_effect = walk_side_effect

        r.resolve("417.1500", self.device)

        def walk_side_effect(arg):
            if (arg == ".1.3.6.1.2.1.17.1.4.1.2"):
                return None
            else:
                return {"136314880": 285421568, "136314912": 285421568}

        r.cache = dict()
        self.device.snmp.walk.side_effect = walk_side_effect
        r.resolve("417.1500", self.device)

    def test_IsamOldOctets_resolver_new_baseport(self):
        r = i.IsamOldOctets(dict())

        def walk_side_effect(arg):
            if (arg == ".1.3.6.1.2.1.17.1.4.1.2"):
                return {"417": 136314880}
            else:
                return {"136314880": 285421568, "136314912": 285421568}

        self.device.snmp.walk = Mock()
        self.device.snmp.walk.side_effect = walk_side_effect

        r.resolve("417.1500", self.device)

        def walk_side_effect(arg):
            if (arg == ".1.3.6.1.2.1.17.1.4.1.2"):
                return {"417": 136314880, "418": 136314912}
            else:
                return {"136314880": 285421568, "136314912": 285421568}

        self.device.snmp.walk.side_effect = walk_side_effect
        tags = r.resolve("418.1500", self.device)
        eq_('1/1/4/1', tags["interface"])

