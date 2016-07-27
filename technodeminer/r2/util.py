import os
from lxml import etree

def get_filenames(dir):
    out_filenames = []
    for root, dirs, filenames in os.walk(dir):
        for f in filenames:
            out_filenames.append(os.path.join(root,f))
    return out_filenames


def strip_xml(filename):
    tree = etree.parse(filename)
    notags = etree.tostring(tree, encoding='utf-8', method='text')
    return unicode(notags, "utf-8")
