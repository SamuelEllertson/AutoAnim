from operator import itemgetter

class State:

    extension = "png"

    def __init__(self, data):

        if data is None:
            self.data = dict()

        elif isinstance(data, dict):
            self.data = data.copy()

    def __repr__(self):
        return repr(self.data)

    def __hash__(self):
        return hash(self.canonical_name)

    def __eq__(self, other):
        return type(self) == type(other) and self.canonical_name == other.canonical_name

    def __iter__(self):
        return iter(self.data.items())

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

    def validate(self, psd_groups):
        for key, value in self.data.items():
            if key not in psd_groups:
                raise KeyError(f"Received invalid key value: {key}:{value}")

            if value not in psd_groups[key]:
                raise ValueError(f"Received invalid option value: {key}:{value}")

        undefined_keys = set(psd_groups.keys()) - set(self.data.keys())

        if len(undefined_keys) != 0:
            raise ValueError(f"All settings must be specified during the first frame. Currently missing: {undefined_keys!r}")