from opentsdb.snmp.resolvers.ifname import IfName
from nose.tools import ok_, eq_
from mock import Mock


class ifname_tests(object):
    def setup(self):
        self.device = Mock()
        self.device.hostname = "foobar"
        self.device.snmp = Mock()
        self.device.snmp.walk = Mock(return_value={1: "eth0", 2: "eth1"})

    def test_resolve(self):
        r = IfName()
        # cache is empty
        ok_(not IfName.cache)
        ret = r.resolve(1, self.device)
        ok_("foobar" in IfName.cache)
        self.device.snmp.walk = Mock(side_effect=Exception())
        eq_("eth0", ret)
        eq_("eth1", r.resolve(2, self.device))
