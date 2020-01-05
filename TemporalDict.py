
from collections import defaultdict
from operator import itemgetter

class TemporalDict:
    def __init__(self):
        self.data = defaultdict(dict)
        self._sorted_data = None
        self.dirty = True

    def add_entry(self, options, time):
        self.data[time].update(options)
        self.dirty = True

    @property
    def sorted_data(self):

        if self._sorted_data is not None and not self.dirty:
            return self.sorted_data

        self._sorted_data = sorted(self.data.items(), key=itemgetter(0))

        return self._sorted_data

    def __len__(self):
        return len(self.data)
    
    @property
    def min_time(self):
        return self.sorted_data[0][0] 

    @property
    def max_time(self):
        return self.sorted_data[-1][0]

    def __getitem__(self, key):
        if not isinstance(key, slice):
            return self.data[key]

        return list(item[1] for item in filter( (lambda x: key.start <= x[0] < key.stop), self.sorted_data)) ###This can be optimized to take advantaged of the sorted data



