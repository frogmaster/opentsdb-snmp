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
from nose.tools import eq_
from opentsdb.snmp.resolvers.isam_xdsl import IsamNFXSB, IsamNFXSA, IsamOld


class TestISAM(object):
    def test_IsamNFXSB_resolver(self):
        resolver = IsamNFXSB()
        testdata = [
            {"index": 67108864,  "expected": "1/1/4/1"},
            {"index": 67125248,  "expected": "1/1/4/3"},
            {"index": 67493888,  "expected": "1/1/4/48"},
            {"index": 134217728, "expected": "1/1/6/1"},
            {"index": 134455296, "expected": "1/1/6/30"},
            {"index": 536920064, "expected": "2/1/1/7"},
            {"index": 537247744, "expected": "2/1/1/47"},
            {"index": 604028928, "expected": "2/2/1/7"},
            {"index": 671277056, "expected": "2/3/1/24"},
        ]

        for item in testdata:
            tags = resolver.resolve(item["index"])
            eq_(item["expected"], tags["interface"])

    def test_IsamNFXSA_resolver(self):
        resolver = IsamNFXSA()
        testdata = [
            {"index": 67231744, "expected": "1/1/1/16"},
            {"index": 101048320, "expected": "1/1/2/48"},
            {"index": 302333952, "expected": "1/1/8/43"},
            {"index": 335929344, "expected": "1/1/12/48"},
            {"index": 570425344, "expected": "1/1/19/1"},
        ]

        for item in testdata:
            tags = resolver.resolve(item["index"])
            eq_(item["expected"], tags["interface"])

    def test_IsamOld_resolver(self):
        resolver = IsamOld()
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
