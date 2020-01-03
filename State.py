from operator import itemgetter

class State:

    extension = "png"

    def __init__(self, duration=200, options=None, data=None):
                
        self.duration = duration

        if data is None:
            self.data = dict()

        elif isinstance(data, dict):
            self.data = data.copy()

        elif isinstance(data, State):
            self.data = data.data.copy()

        if options is not None:
            data.update(self.strings_to_dict(options))

    def __repr__(self):
        return f"State(duration={self.duration}, options={self.data!r})"

    def __hash__(self):
        return hash(frozenset(self.data.items()))

    def strings_to_dict(self, options):

        new_dict = dict()

        if options is None:
            return new_dict

        #List of options strings not necessarily consistent, so concat then split first.
        option_pairs = ",".join(options).split(",")

        for pair in option_pairs:
            key, value = pair.split(":")

            new_dict[key.strip()] = value.strip()

        return new_dict

    def add_options(self, options):

        if isinstance(options, str):
            options = [options]

        self.data.update(self.strings_to_dict(options))

    @property
    def filename(self):
        return f"{self.canonical_name}.{self.extension}"

    @property
    def canonical_name(self):
        '''Canonical name is lowercase key-value pairs seperated by underscores _ sorted by the key'''

        parts = []

        items = list(self.data.items())
        items.sort(key=itemgetter(0))

        for key, value in items:
            key   = key.lower().strip()
            value = value.lower().strip()

            parts.append(f"{key}-{value}")

        return "_".join(parts)