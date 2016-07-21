import requests
from collections import Sequence
from lxml import html
from technodeminer.util import nonelessdict

# pre-~2014-ish
class OldHTMLSolicitationReader(Sequence):
    def __init__(self, tree):
        self.tree = tree
        self.elems = self.get_solicitation_elems()
        self.solicitations = self.build_solicitations(self.elems)

    @staticmethod
    def from_htmlfile(filename):
        tree = html.parse(filename)
        return OldHTMLSolicitationReader(tree)

    @staticmethod
    def from_htmlurl(url):
        resp = requests.get(url)
        tree = html.fromstring(resp.content)
        return OldHTMLSolicitationReader(tree)

    def get_solicitation_elems(self):
        xpath = "//p/b/span[contains(.,'Topic Descriptions')]/ancestor::p/following-sibling::*"
        elems = self.tree.xpath(xpath)
        return elems
        #[elem.xpath('span')[0].text for elem in elems]


    @staticmethod
    def remove_nbsp(str):
        return str.replace(u'\xa0', u' ')

    @staticmethod
    def is_str_empty(str):
        str = OldHTMLSolicitationReader.remove_nbsp(str)
        return (str.strip() == '')

    @staticmethod
    def build_solicitations(elems):
        solicitations = []
        solicitation = []
        for elem in elems:
            solicitation += elem
            if elem.xpath('span')[0].text.startswith("KEYWORDS: "):
                solicitations.append(solicitation)
                solicitation = [] # zero out
        return solicitations


    def __getitem__(self, item):
        return self.solicitations[item]


    def __len__(self):
        return len(self.solicitations)


    def __iter__(self):
        return iter(self.solicitations)


class HTMLSolicitationReader(Sequence):
    def __init__(self, tree):
        self.tree = tree
        self.elems = self.get_solicitation_elems()
        # could do this lazily but they're so small why bother...
        self.solicitations = self.make_solicitations()

    @staticmethod
    def from_htmlfile(filename):
        tree = html.parse(filename)
        return HTMLSolicitationReader(tree)

    @staticmethod
    def from_htmlstr(str):
        tree = html.fromstring(str)
        return HTMLSolicitationReader(tree)

    @staticmethod
    def from_htmlurl(url):
        resp = requests.get(url)
        tree = html.fromstring(resp.content)
        return HTMLSolicitationReader(tree)


    def get_solicitation_elems(self):
        # this gives list of divs
        xpath = "//div[preceding-sibling::comment()[. = ' begin-topic-desc ']]" \
                     "[following-sibling::comment()[. = ' end-topic-desc ']]"
        elems = self.tree.xpath(xpath)
        return elems[1:]  # first one is a header


    def __getitem__(self, item):
        return self.solicitations[item]


    def __len__(self):
        return len(self.solicitations)


    def __iter__(self):
        return iter(self.solicitations)

    @staticmethod
    def get_description(elem):
        # Description / Phases
        desc_elems = elem.xpath("p[preceding-sibling::p[starts-with(.,'OBJECTIVE:')]]"
                                "[following-sibling::p[starts-with(.,'REFERENCES:')]]")
        description = ""
        for desc in desc_elems:
            description += desc.text
        return description

    @staticmethod
    def get_references(elem):
        # List of references
        try:  # also optional..
            references = list()
            ref_list = elem.xpath("ul[preceding-sibling::p[. = 'REFERENCES:']]")[0]
            for ref in ref_list.xpath("li"):
                references.append(ref.text)
            return references
        except IndexError:
            return None


    @staticmethod
    def process_tech_area_str(str):
        tech_areas = str[20:].split(",")
        tech_areas = [x.strip() for x in tech_areas]
        return tech_areas

    @staticmethod
    def get_techareas(elem):
        try:
            tech_areas = elem.xpath("p[starts-with(.,'TECHNOLOGY AREA')]")[0].text
            return HTMLSolicitationReader.process_tech_area_str(tech_areas)
        except IndexError:
            return None

    @staticmethod
    def get_objective(elem):
        try:
            objective = elem.xpath("p[starts-with(.,'OBJECTIVE:')]")[0].text
            return objective[11:]
        except IndexError:
            return None

    @staticmethod
    def get_keywords(elem):
        # Keywords (cf. tech areas)
        try:  # turns out this is optional
            keywords_str = elem.xpath("p[starts-with(.,'KEYWORDS:')]")[0].text
            keywords = list()
            for kw in keywords_str[10:].split(","): keywords.append(kw.strip())
            return keywords
        except IndexError:
            return None

    def make_solicitations(self):
        broken_topic = False  # Not really a fan of this.. will refactor if we find more
        solicitations = list()
        for elem in self.elems:
            if len(elem.xpath('div')) > 0:
                sol = nonelessdict()
                sol['topic'] = elem.xpath('div')[0].text
                title = elem.xpath('div')[1].text
                if title.startswith("OBJECTIVE"): # some are messed up like this, e.g. af161
                    sol['objective'] = title
                    sol['tech_areas'] = self.process_tech_area_str(elem.xpath('div')[0].text)
                    sol['topic'] = "ERROR: Malformed Topic"
                    sol['title'] = "ERROR: Malformed Title"
                    broken_topic = True
                if not any(s in title for s in ["has been removed","has been deleted"]):
                    sol['references'] = self.get_references(elem)
                    sol['description'] = self.get_description(elem)
                    sol['keywords'] = self.get_keywords(elem)
                    if not broken_topic:
                        sol['title'] = title[7:]
                        sol['objective'] = self.get_objective(elem)
                        sol['tech_areas'] = self.get_techareas(elem)

                    solicitations.append(sol)
        return solicitations




