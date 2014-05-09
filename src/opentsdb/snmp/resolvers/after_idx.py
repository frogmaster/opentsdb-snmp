class AfterIndex:
    def resolve(self, index, device=None):
        tags = {}
        buf = ("%s" % index).split(".")
        tags["index"] = int(buf[0])
        if int(buf[1]) == 2:
            tags["direction"] = "out"
        elif int(buf[1]) == 1:
            tags["direction"] = "in"
        else:
            raise Exception("Direction after Index Resolve failed")
        return tags
