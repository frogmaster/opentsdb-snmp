from nose.tools import eq_
from opentsdb.snmp.resolvers.d500_xdsl import D500_xdsl


class TestDevice(object):
    def test_d500_xdsl_resolver(self):
        resolver = D500_xdsl()
        tags = resolver.resolve(1101)
        eq_("11/1", tags["interface"])
        tags = resolver.resolve(711)
        eq_("7/11", tags["interface"])
