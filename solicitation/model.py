from lxml import html

class SolicitationReader(object):
    def __init__(self, filename):
        self.tree = html.parse(filename)

    def get_num_solicitations(self):
        xpath = ".//body/div/table/tbody/tr"
        return len(self.tree.findall(xpath))

    def get_solicitation(self):
        xpath = ".//node()[preceding-sibling::comment()[. = '001']]"

    #// comment()[contains(., 'family names')] / following::*[not (preceding::comment()[contains(., 'family ends')])]

    def get_solicitations(self):
        pass
class Solicitation(object):
    @staticmethod
    def from_file(filename):
        tree = html.parse(filename)
        return Solicitation(tree)

    @staticmethod
    def from_str(str):
        tree = html.fromstring(str)
        return Solicitation(tree)


    def __init__(self, tree):
        self.root = tree.getroot()

