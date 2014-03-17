from nose.tools import eq_
from opentsdb.snmp.device import Device, default_resolver

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

    def test_get_opentsdb_metrics(self):
       NotImplemented
