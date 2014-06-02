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
            Version=self.version,
            UseNumeric=1,
            Timeout=1000000,
            Retries=0,
        )

    def walk_v1(self, oid, stripoid=True):
        vb = Varbind(oid)
        vl = VarList(vb)
        self.session.walk(vl)
        ret = {}
        for v in vl:
            if v.tag is None:
                continue
            full_oid = v.tag
            if v.iid or v.iid == 0:
                full_oid = v.tag + "." + v.iid
            if stripoid:
                full_oid = full_oid.replace(oid, '')
                full_oid = full_oid.replace(".", '')
            ret[full_oid] = v.val
        return ret

    def walk(self, oid, stripoid=True):
        ret = {}
        startindexpos = 0
        runningtreename = oid

        while (runningtreename == oid):
            vrs = VarList(Varbind(oid, startindexpos))
            result = self.session.getbulk(0, 30, vrs)
            if not result:
                break
            """ Print output from running getbulk"""
            for i in vrs:
                full_oid = i.tag
                if i.tag != oid:
                    runningtreename = i.tag
                    break
                if i.iid or i.iid == 0:
                    full_oid = i.tag + "." + i.iid
                if stripoid:
                    full_oid = full_oid.replace(oid, '')
                    full_oid = full_oid.replace(".", '')
                ret[full_oid] = i.val
            """ Set startindexpos for next getbulk """
            if not vrs[-1].iid:
                break
            startindexpos = int(vrs[-1].iid)
            """ Refresh runningtreename from last result"""
            runningtreename = vrs[-1].tag

        return ret

    def get(self, oid):
        return self.session.get(oid)[0]
