import os
from lxml import etree

def get_filenames(dir):
    filenames = list()
    for root, dirs, filenames in os.walk(dir):
        for f in filenames:
            filenames.append(f)
    return filenames


def strip_xml(filename):
    tree = etree.parse(filename)
    notags = etree.tostring(tree, encoding='utf-8', method='text')
    return unicode(notags, "utf-8")
