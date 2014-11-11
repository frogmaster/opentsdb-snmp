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
from opentsdb.snmp.value_modifiers.rate import Rate
from nose.tools import ok_, eq_


class rate_tests(object):
    def test_modify(self):

        m = Rate(dict())
        # cache is empty
        ok_(not m.cache)
        result = m.modify(key="foo", ts=100, value=1000)
        ok_(result is None)
        ok_("rate_foo" in m.cache)
        eq_(100, m.cache["rate_foo"]["ts"])
        eq_(1000, m.cache["rate_foo"]["value"])
        result = m.modify(key="foo", ts=200, value=2000)
        eq_(10, result)

        #test counter wraps...
        m.modify(key="foo", ts=300, value=((2 ** 32) - 500))
        result = m.modify(key="foo", ts=400, value=500)
        eq_(10, result)
        #test zero rate:
        result = m.modify(key="foo", ts=500, value=500)
        eq_(0, result)
