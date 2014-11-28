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
import time
from nose.tools import eq_
from mock import Mock, patch
from opentsdb.snmp.main import Main
from opentsdb.snmp.device import Device
from opentsdb.snmp.metric import Metric


class TestDevice(object):
    def setup(self):
        d = {
            'hostname': 'foobar',
            'community': 'public',
            'snmp_version': 2,
            'metrics': ["ifInUcastPkts"]
        }
        main = Main(conf="misc/sample_conf.yml")
        main.load_resolvers()
        self.tested = Device(d, main.resolvers,
                             main.value_modifiers, main.conf.metrics())

    def teardown(self):
        self.tested = None

    def test_it_loaded_data(self):
        eq_('foobar', self.tested.hostname)
        eq_(1, len(self.tested.metrics))


class TestMetric(object):
    def setup(self):
        snmp = Mock()
        snmp.walk = Mock(return_value={
            "1": 10,
            "2": 20,
        })
        snmp.get = Mock(return_value=123)
        self.time = time.time()
        main = Main()
        main.load_resolvers()
        self.mockdevice = Mock()
        self.mockdevice.hostname = "foo"
        self.mockdevice.snmp = snmp
        self.mockdevice.resolvers = main.resolvers

    @patch('time.time')
    def test_opentsdb_walk_metric(self, mocktime):
        mocktime.return_value = self.time
        mdata = {
            'metric': 'interface.packets',
            'oid': '.1.3.6.1.2.1.31.1.1.1.9',
            'type': 'walk',
            'multiply': '0.1',
            'tags': {
                'direction': "in",
                'type': 'broadcast'
            },
            'resolver': 'cisco_ifname'
        }
        m = Metric(
            data=mdata,
            device=self.mockdevice
        )
        #test _tags_to_str with empty tags
        eq_("host=foo", m._tags_to_str({}))
        walkdata = m._get_walk(self.mockdevice.snmp)
        eq_(10, walkdata["1"])
        eq_(20, walkdata["2"])
        eq_(
            "put interface.packets "
            + str(int(self.time)) +
            " 2.0 host=foo index=2 direction=in type=broadcast",
            m._process_dp(20, 2)
        )
        result = m._process_walk_data(walkdata)
        eq_(2, len(result))
        eq_(
            'put interface.packets '
            + str(int(self.time)) +
            ' 1.0 host=foo index=1 direction=in type=broadcast',
            result[0]
        )
        result = m.get_opentsdb_commands(self.mockdevice.snmp)
        eq_(2, len(result))
        eq_(
            'put interface.packets '
            + str(int(self.time)) +
            ' 1.0 host=foo index=1 direction=in type=broadcast',
            result[0]
        )

    @patch('time.time')
    def test_opentsdb_get_metric(self, mocktime):
        mocktime.return_value = self.time
        mdata = {
            'metric': 'cpmCPUTotal5minRev',
            'oid': '.1.3.6.1.4.1.9.9.109.1.1.1.1.8',
            'type': 'get',
            'tags': {},
        }
        m = Metric(
            data=mdata,
            device=self.mockdevice
        )
        result = m.get_opentsdb_commands(self.mockdevice.snmp)[0]
        eq_(
            "put cpmCPUTotal5minRev "
            + str(int(self.time)) +
            " 123 host=foo",
            result
        )
