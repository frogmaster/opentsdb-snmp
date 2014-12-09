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
import opentsdb.snmp.resolvers.huawei as hw
from mock import Mock


class TestHuawei(object):
    def setup(self):
        self.device = Mock()
        self.device.hostname = "foobar"
        self.device.snmp = Mock()

    def test_index_to_name(self):
        r = hw._Huawei()
        eq_("0/7/3", r.index_to_name(234938560), "Ethernet interface")
        eq_("0/5/63", r.index_to_name(4160794560), "VDSL interface")
        xdsl_idx = 4160794560 - 33554431
        eq_("0/5/63", r.index_to_name(xdsl_idx), "XDSL interface")
        eq_("0/4/7", r.index_to_name(4194338560), "GPON interface")

    def test_huawei_ifname(self):
        r = hw.HuaweiIfName()
        tags = r.resolve(4160794560, device=self.device)
        eq_(tags["index"], 4160794560)
        eq_(tags["interface"], "0/5/63")

    def test_huawei_after_idx(self):
        r = hw.HuaweiAfterIndex()
        tags = r.resolve("4160794560.2", device=self.device)
        eq_(tags["index"], 4160794560)
        eq_(tags["direction"], "out")
        eq_(tags["interface"], "0/5/63")

    def test_huawei_ont(self):
        r = hw.HuaweiOnt()
        tags = r.resolve("4160794560.14.0")
        eq_(tags["index"], "4160794560.14.0")
        eq_(tags["interface"], "0/5/63")
        eq_(tags["ont"], "14")
        eq_(tags["ontport"], "0")
