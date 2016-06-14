from collections import Sequence
from lxml import html
from technodeminer.util import nonelessdict


class SolicitationReader(Sequence):
    def __init__(self, filename):
        self.tree = html.parse(filename)
        self.elems = self.get_solicitation_elems()
        # could do this lazily but they're so small why bother...
        self.solicitations = self.make_solicitations()

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


    def make_solicitations(self):
        solicitations = list()
        for elem in self.elems:
            sol = nonelessdict()
            sol['topic'] = elem.xpath('div')[0].text
            sol['title'] = elem.xpath('div')[1].text[7:]

            # Tech areas
            tech_areas = elem.xpath("p[starts-with(.,'TECHNOLOGY AREA')]")[0].text
            if tech_areas:
                sol['tech_areas'] = tech_areas[20:].split(",")
                sol['tech_areas'] = [x.strip() for x in sol['tech_areas']]
            # List of references
            sol['references'] = list()
            ref_list = elem.xpath("ul[preceding-sibling::p[. = 'REFERENCES:']]")[0]
            for ref in ref_list.xpath("li"):
                sol['references'].append(ref.text)

            # Description / Phases
            desc_elems = elem.xpath("p[preceding-sibling::p[starts-with(.,'OBJECTIVE:')]]"
                                     "[following-sibling::p[starts-with(.,'REFERENCES:')]]")
            sol['description'] = ""
            for desc in desc_elems:
                sol['description'] += desc.text
            # Keywords (cf. tech areas)
            keywords = elem.xpath("p[starts-with(.,'KEYWORDS:')]")[0].text
            sol['keywords'] = list()
            for kw in keywords[10:].split(","): sol['keywords'].append(kw.strip())
            # Objective
            objective = elem.xpath("p[starts-with(.,'OBJECTIVE:')]")[0].text
            if objective: sol['objective'] = objective[11:]

            solicitations.append(sol)
        return solicitations




