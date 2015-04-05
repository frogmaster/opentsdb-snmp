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
import sys
sys.modules['netsnmp'] = Mock()
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
        snmp.bulkwalk = Mock(return_value={
            "1": 10,
            "2": 20,
            "3": 0,
        })
        snmp.get = Mock(return_value=123)
        self.time = time.time()
        main = Main()
        main.load_resolvers()
        self.mockdevice = Mock()
        self.mockdevice.hostname = "foo"
        self.mockdevice.snmp = snmp
        self.mockdevice.resolvers = main.resolvers
        self.walkmetric = {
            'metric': 'interface.packets.{direction}.{host}',
            'oid': '.1.3.6.1.2.1.31.1.1.1.9',
            'type': 'bulkwalk',
            'multiply': '0.1',
            'tags': {
                'direction': "in",
                'type': 'broadcast'
            },
            'resolver': 'default'
        }

    @patch('time.time')
    def test_opentsdb_walk_metric(self, mocktime):
        mocktime.return_value = self.time
        metric = self.walkmetric
        metric["device"] = self.mockdevice
        m = Metric(**metric)
        #test _tags_to_str with empty tags
        eq_("", m._tags_to_str({}))
        walkdata = m._get_walk(self.mockdevice.snmp)
        eq_(10, walkdata["1"])
        eq_(20, walkdata["2"])
        eq_(0,  walkdata["3"])
        eq_(
            "put interface.packets.in.foo "
            + str(int(self.time)) +
            " 2.0 index=2 type=broadcast",
            m._process_dp(20, self.time, key=2)
        )
        result = m._process_walk_data(walkdata, self.time)
        eq_(3, len(result))
        eq_(
            'put interface.packets.in.foo '
            + str(int(self.time)) +
            ' 1.0 index=1 type=broadcast',
            result[0]
        )
        result = m.get_opentsdb_commands(self.mockdevice.snmp, self.time)
        eq_(3, len(result))
        eq_(
            'put interface.packets.in.foo '
            + str(int(self.time)) +
            ' 1.0 index=1 type=broadcast',
            result[0]
        )

    def test_opentsdb_walk_metric_with_ranges(self):
        mdata = self.walkmetric
        mdata["min_val"] = 10
        mdata["max_val"] = 19
        mdata["device"] = self.mockdevice
        m = Metric(
            **mdata
        )
        walkdata = m._get_walk(self.mockdevice.snmp)
        result = m._process_walk_data(walkdata, self.time)
        eq_(1, len(result))

    def test_opentsdb_walk_metric_with_replacement(self):
        mdata = self.walkmetric
        mdata["min_val"] = 10
        mdata["max_val"] = 19
        mdata["replacement_val"] = 0
        mdata["device"] = self.mockdevice
        m = Metric(
            **mdata
        )
        walkdata = m._get_walk(self.mockdevice.snmp)
        result = m._process_walk_data(walkdata, self.time)

        eq_(3, len(result))

    @patch('time.time')
    def test_opentsdb_get_metric(self, mocktime):
        mocktime.return_value = self.time
        mdata = {
            'metric': 'cpmCPUTotal5minRev',
            'oid': '.1.3.6.1.4.1.9.9.109.1.1.1.1.8',
            'type': 'get',
            'tags': {},
            'device': self.mockdevice,
        }
        m = Metric(
            **mdata
        )
        result = m.get_opentsdb_commands(self.mockdevice.snmp, self.time)[0]
        eq_(
            "put cpmCPUTotal5minRev "
            + str(int(self.time)) +
            " 123 host=foo",
            result
        )
