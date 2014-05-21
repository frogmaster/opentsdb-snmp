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
