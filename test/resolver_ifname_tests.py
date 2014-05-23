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
from opentsdb.snmp.resolvers.ifname import IfName
from nose.tools import ok_, eq_
from mock import Mock


class ifname_tests(object):
    def setup(self):
        self.device = Mock()
        self.device.hostname = "foobar"
        self.device.snmp = Mock()
        self.device.snmp.walk = Mock(return_value={"1": "eth0", "2": "eth1"})

    def test_resolve(self):
        r = IfName()
        # cache is empty
        ok_(not IfName.cache)
        ret = r.resolve("1", self.device)
        ok_("foobar" in IfName.cache)
        #throw exceprion if the value is not taken from cache
        self.device.snmp.walk = Mock(side_effect=Exception())
        eq_("eth0", ret["interface"])
        eq_("eth1", r.resolve("2", self.device)["interface"])
