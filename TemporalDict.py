
from collections import defaultdict
from operator import itemgetter
from State import State

class TemporalDict:
    def __init__(self, args):
        self.args = args
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
    
    @property
    def states(self):
        current_state = {}

        frame_time = self.args.speed_multiplier / self.args.fps * 1000
        
        start, stop = self.min_time - frame_time / 2, self.min_time + frame_time / 2

        while start <= self.max_time:

            for state in self[start:stop]:
                current_state.update(state)

            state_obj = State(current_state)

            yield state_obj

            start, stop = stop, stop + frame_time

    def print(self):
        for index, state in enumerate(self.states):
            print(f"Frame {index}: {state!r}")

