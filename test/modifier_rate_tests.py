from opentsdb.snmp.value_modifiers.rate import Rate
from nose.tools import ok_, eq_


class rate_tests(object):
    def test_modify(self):
        m = Rate()
        # cache is empty
        ok_(not Rate.cache)
        result = m.modify(key="foo", ts=100, value=1000)
        ok_(result is None)
        ok_("foo" in Rate.cache)
        eq_(100, Rate.cache["foo"]["ts"])
        eq_(1000, Rate.cache["foo"]["value"])
        result = m.modify(key="foo", ts=200, value=2000)
        eq_(10, result)

        #test counter wraps...
        m.modify(key="foo", ts=300, value=((2 ** 32) - 500))
        result = m.modify(key="foo", ts=400, value=500)
        eq_(10, result)
