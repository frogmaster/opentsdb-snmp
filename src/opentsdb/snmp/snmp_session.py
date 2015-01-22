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
from socket import gethostbyname
import logging


class SNMPSession:
    def __init__(self, host, community, version=2, timeout=2000000, retries=0):
        self.session = None
        self.host = host
        self.community = community
        self.version = version
        self.timeout = timeout
        self.retries = retries

    def connect(self):
        #resolve hostname
        try:
            ip = gethostbyname(self.host)
        except:
            self.session = None
            return None
        self.session = Session(
            DestHost=ip,
            Community=self.community,
            Version=self.version,
            UseNumeric=1,
            Timeout=self.timeout,
            Retries=self.retries,
        )

    def walk(self, oid, stripoid=True, expect_str=False):
        vb = Varbind(oid)
        vl = VarList(vb)
        self.session.walk(vl)
        ret = {}
        for v in vl:
            if v.tag is None:
                continue
            full_oid = v.tag
            (full_oid, val) = handle_vb(v, expect_str)
            if stripoid:
                full_oid = full_oid.replace(oid + ".", '')
            ret[full_oid] = val
        return ret

    def bulkwalk(self, oid,
                 stripoid=True, startidx=None,
                 endidx=None, expect_str=False):
        ret = {}
        if oid[0] != ".":
            oid = "." + oid
        startindexpos = startidx
        runningtreename = oid
        stop = False

        while (runningtreename.startswith(oid) and stop is False):
            vrs = VarList(Varbind(oid, startindexpos))
            result = self.session.getbulk(0, 100, vrs)
            if self.session.ErrorInd:
                logging.warn(
                    "walk failed on: {0} ({1})".format(
                        self.host, self.session.ErrorStr
                    )
                )
            key = None
            if not result:
                break
            """ Print output from running getbulk"""
            for i in vrs:
                if endidx and int(i.iid) > int(endidx):
                    stop = True
                    break
                if not i.tag.startswith(oid):
                    break
                (full_oid, val) = handle_vb(i, expect_str)
                key = full_oid.replace(oid + ".", "")
                if stripoid:
                    ret[key] = val
                else:
                    ret[full_oid] = val
            """ Set startindexpos for next getbulk """
            if not vrs[-1].iid or not key or stop:
                break
            startindexpos = int(key.split(".")[0])
            """ Refresh runningtreename from last result"""
            runningtreename = vrs[-1].tag

        return ret

    def get(self, oid):
        return self.session.get(oid)[0]


def handle_vb(vb, expect_str):
    if vb.iid or vb.iid == 0:
        full_oid = vb.tag + "." + vb.iid
    else:
        full_oid = vb.tag
    if vb.type == "OCTETSTR" and not expect_str:
        return (full_oid, int(vb.val.encode("hex"), 16))
    else:
        return (full_oid,  vb.val)
