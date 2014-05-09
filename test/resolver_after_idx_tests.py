from nose.tools import eq_
from opentsdb.snmp.resolvers.after_idx import AfterIndex


class TestDevice(object):
    def test_after_index_resolver(self):
        resolver = AfterIndex()
        tags = resolver.resolve("123.2")
        eq_(123, tags["index"])
        eq_('out', tags["direction"])
        tags = resolver.resolve("123.1")
        eq_('in', tags["direction"])
