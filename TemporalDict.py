
from collections import defaultdict
from operator import itemgetter

from State import State

class TemporalDict:
    def __init__(self):
        self.data = defaultdict(dict)

    def add_entry(self, options, time):
        self.data[time].update(options)

    def get_sorted_items(self):
        return sorted(self.data.items(), key=itemgetter(0))

    def __iter__(self):
        sorted_items = self.get_sorted_items()

        options = {}
        rollover_time = 0

        for (time_prev, state_dict_prev), (time_next, state_dict_next) in zip(sorted_items, sorted_items[1:]):
            
            duration = time_next - time_prev

            if options.copy().update(state_dict_prev) == options:
                rollover_time += duration
                continue

            duration += rollover_time
            rollover_time = 0

            options.update(state_dict_prev)

            yield State(duration=duration, data=options)

