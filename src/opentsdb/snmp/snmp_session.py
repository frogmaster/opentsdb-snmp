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
