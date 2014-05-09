from nose.tools import eq_
from opentsdb.snmp.resolvers.default import Default


class TestDevice(object):
    def test_default_resolver(self):
        resolver = Default()
        tags = resolver.resolve("123.3")
        eq_(123, tags["index"])
        eq_(3, tags["index2"])
