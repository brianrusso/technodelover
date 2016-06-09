from lxml import etree
from pattern.en import parsetree
from pattern.search import search
from textblob import TextBlob as tb
import os
from textblob.classifiers import NaiveBayesClassifier

R2_DIR = "/media/sf_Data/CTV_R2"
SEMANTIC_PATTERNS = ['JJ NP', 'NN NNS', 'JJ NN NNS']

r2_training = [('procurement', 'budget'),
               ('contracts', 'budget'),
               ('fixed-price','budget'),
               ('funding','budget'),
               ('cost-type', 'budget'),
               ('cost','budget'),
               ('mission','tech'),
               ('laser','tech'),
               ('systems', 'tech'),
               ('propulsion','tech'),
               ('warfare','tech')
               ]


def get_filenames(dir):
    filenames = list()
    for root, dirs, filenames in os.walk(dir):
        for f in filenames:
            filenames.append(f)
    return filenames


def r2_to_obj(filename):
    tree = etree.parse(filename)
    root = tree.getroot()
    mission_descs = root.findall("r2:ProgramElementMissionDescription", root.nsmap)


def r2_to_txt(filename):
    tree = etree.parse(filename)
    notags = etree.tostring(tree, encoding='utf-8', method='text')
    return unicode(notags, "utf-8")



def terms_in_txt(text, semantic_patterns):
    pt = parsetree(text)
    techterms = set()
    for pattern in SEMANTIC_PATTERNS:
        techterms.add(search(pattern, pt).string)
    return techterms

if __name__ == '__main__':
    r2txt = r2_to_txt('/media/sf_Data/CTV_R2/U_1160401BB_2_PB_2017.xml')
    print terms_in_txt(r2txt, SEMANTIC_PATTERNS)

namespaces = {'r2':'http://www.dtic.mil/comptroller/xml/schema/022009/r2'}