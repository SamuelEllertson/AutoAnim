from operator import itemgetter

class State:

    extension = "png"

    def __init__(self, data):

        if data is None:
            self.data = dict()

        elif isinstance(data, dict):
            self.data = data.copy()

    def __repr__(self):
        return f"State(options={self.data!r})"

    def __hash__(self):
        return hash(frozenset(self.data.items()))

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