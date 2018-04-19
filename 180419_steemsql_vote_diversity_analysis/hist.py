#!/usr/bin/python


class hist:
    def __init__(self):
        self.hist = {}
        self.list_of_values = {}
        self.nentries = 0

    def fill(self, key, incr=1):
        if key not in self.hist:
            self.hist[key] = 0
            self.list_of_values[key] = []
        self.hist[key] += incr
        self.list_of_values[key].append(incr)
        self.nentries += 1

    def xrange(self, sort='value'):
        if sort != 'value':
            return [x for x in sorted(self.hist, reverse=True)]
        else:
            return [x for x in sorted(self.hist, key=lambda k:
                                      self.hist[k], reverse=True)]

    def yrange(self, sort='value'):
        if sort != 'value':
            return [self.hist[x] for x in sorted(self.hist,
                                                 reverse=True)]
        else:
            return [self.hist[x] for x in sorted(self.hist, key=lambda
                                                 k: self.hist[k],
                                                 reverse=True)]
