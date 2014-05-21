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
from netsnmp import Session, Varbind, VarList


class SNMPSession:
    def __init__(self, host, community, version=2):
        self.session = None
        self.host = host
        self.community = community
        self.version = version

    def connect(self):
        self.session = Session(
            DestHost=self.host,
            Community=self.community,
            Version=self.version
        )

    def walk(self, oid, stripoid=True):
        if not self.session:
            self.connect()

        vb = Varbind(oid)
        vl = VarList(vb)
        self.session.walk(vl)
        ret = {}
        for v in vl:
            full_oid = v.tag
            if v.iid or v.iid == 0:
                full_oid = v.tag + "." + v.iid
            if stripoid:
                full_oid = full_oid.replace(oid, '')
                full_oid = full_oid.replace(".", '')
            ret[full_oid] = v.val
        return ret

    def get(self, oid):
        if not self.session:
            self.connect()
        return self.session.get(oid)[0]
