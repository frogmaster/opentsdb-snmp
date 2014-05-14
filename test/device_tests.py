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
            'metrics': [
                {
                    'metric': 'interface.packets',
                    'oid': '.1.3.6.1.2.1.31.1.1.1.9',
                    'type': 'walk',
                    'tags': {
                        'direction': "in",
                        'type': 'broadcast'
                    },
                }
            ]
        }
        main = Main()
        main.load_resolvers
        self.tested = Device(d, main.resolvers, main.value_modifiers)
        d["metrics"][0]["resolver"] = "default"
        self.tested = Device(d, main.resolvers, main.value_modifiers)

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
        self.snmpmock = snmp
        self.time = time.time()
        main = Main()
        main.load_resolvers()
        self.resolvers = main.resolvers

    @patch('time.time')
    def test_opentsdb_walk_metric(self, mocktime):
        mocktime.return_value = self.time
        mdata = {
            'metric': 'interface.packets',
            'oid': '.1.3.6.1.2.1.31.1.1.1.9',
            'type': 'walk',
            'tags': {
                'direction': "in",
                'type': 'broadcast'
            },
            'resolver': 'cisco_ifname'
        }
        m = Metric(
            data=mdata,
            snmp=self.snmpmock,
            resolvers=self.resolvers,
            host="foo"
        )
        #test _tags_to_str with empty tags
        eq_("", m._tags_to_str({}))
        walkdata = m._get_walk()
        eq_(10, walkdata["1"])
        eq_(20, walkdata["2"])
        eq_(
            "put interface.packets "
            + str(int(self.time)) +
            " 20 index=2 direction=in type=broadcast host=foo",
            m._process_dp(20, 2)
        )
        result = m._process_walk_data(walkdata)
        eq_(2, len(result))
        eq_(
            'put interface.packets '
            + str(int(self.time)) +
            ' 10 index=1 direction=in type=broadcast host=foo',
            result[0]
        )
        result = m.get_opentsdb_commands()
        eq_(2, len(result))
        eq_(
            'put interface.packets '
            + str(int(self.time)) +
            ' 10 index=1 direction=in type=broadcast host=foo',
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
            snmp=self.snmpmock,
            resolvers=self.resolvers,
            host='foo'
        )
        result = m.get_opentsdb_commands()[0]
        eq_(
            "put cpmCPUTotal5minRev "
            + str(int(self.time)) +
            " 123 host=foo",
            result
        )
