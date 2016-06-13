class nonelessdict(dict):
    def __setitem__(self, key, value):
        if value is not None:
            dict.__setitem__(self, key, value)
        elif key in self and value is None:
            dict.__delitem__(self, key)