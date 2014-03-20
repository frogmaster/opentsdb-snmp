import time
from nose.tools import eq_
from mock import Mock, patch
from opentsdb.snmp.device import Device, default_resolver
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
                        'resolver': 'cisco_ifname'
                        }
                    ]
                }
        self.tested = Device(d)
    def teardown(self):
        self.tested = None

    def test_it_loaded_data(self):
        eq_('foobar', self.tested.hostname)
        eq_(1, len(self.tested.metrics))

    def test_default_resolver(self):
        resolver = default_resolver()
        tags = resolver.resolve("123.3")
        eq_('123', tags["index"])
        eq_('3', tags["index2"])

class TestMetric(object):
    def setup(self):
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
        snmp = Mock()
        snmp.walk = Mock(return_value={
            "1": 10,
            "2": 20,
        })
        self.tested = Metric(data=mdata, snmp=snmp, resolvers={'default': default_resolver}, host="foo")
        self.time = time.time()

    @patch('time.time')
    def test_opentsdb_walk_metric(self, mocktime):
        m = self.tested
        mocktime.return_value = self.time
        walkdata = m._get_walk()
        eq_(10, walkdata["1"])
        eq_(20, walkdata["2"])
        eq_("put interface.packets "+str(int(self.time))+" 20 index=2 direction=in type=broadcast host=foo", m._process_dp(20, 2))
        result = m._process_walk_data(walkdata)
        eq_(2, len(result))
        eq_('put interface.packets '+str(int(self.time))+' 10 index=1 direction=in type=broadcast host=foo', result[0])
