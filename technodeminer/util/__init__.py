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


# add input to output; given dictionaries where key = ngram, value = count (int)
def add_countdict(outputdict, inputdict):
    for k in inputdict.keys():
        if k in outputdict:
            outputdict[k] += inputdict[k]
        else:
            outputdict[k] = inputdict[k]
    return outputdict


# regularise dictionary
def clean_dict(dict):
    for k in dict.keys():
        cleankey = regularise_key(k)
        if k != cleankey:
            if cleankey in dict:
                dict[cleankey] += dict[k]
                del dict[k]
            else:
                dict[cleankey] = dict[k]
                del dict[k]
    return dict


def dict_to_tuple_list(dict_of_counts):
    count_list = []
    for k in dict_of_counts.keys():
        count_list.append((k, dict_of_counts[k]))
    return count_list

