class nonelessdict(dict):
    def __setitem__(self, key, value):
        if value is not None:
            dict.__setitem__(self, key, value)
        elif key in self and value is None:
            dict.__delitem__(self, key)


def remove_nbsp(str):
    return str.replace(u'\xa0', u' ')

def remove_newlines(str):
    str = str.replace("\r\n"," ")
    return str.replace('\n',' ')


def is_str_empty(str):
    str = remove_nbsp(str)
    return (str.strip() == '')