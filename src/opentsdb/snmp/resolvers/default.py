class Default:
    def resolve(self, index, device=None):
        tags = {}
        buf = ("%s" % index).split(".")
        cnt = 0
        for i in buf:
            if cnt == 0:
                tags["index"] = int(i)
                cnt += 1
            else:
                cnt += 1
                tags["index%d" % cnt] = int(i)
        return tags
