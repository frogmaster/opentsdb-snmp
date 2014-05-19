class D500_xdsl:
    def resolve(self, index, device=None):
        card = int(str(index)[:-2])
        port = int(str(index)[-2:])
        interface = "%d/%d" % (card, port)
        return {"interface": interface}
