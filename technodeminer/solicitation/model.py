import requests
from collections import Sequence
from lxml import html
from technodeminer.util import nonelessdict, remove_nbsp, remove_newlines, is_str_empty
import re

def process_tech_area_str(str):
    tech_areas = str.split(",")
    tech_areas = [x.strip() for x in tech_areas]
    return tech_areas

# pre-~2014-ish
class OldHTMLSolicitationReader(Sequence):
    def __init__(self, tree, listing=None):
        self.tree = tree
        self.elems = self.get_solicitation_elems()
        self.solicitations_raw = self.build_solicitations_raw(self.elems)
        self.solicitations = self.build_solicitations(self.solicitations_raw)
        if listing:
            self.merge_parent_listing_info(listing)

    @staticmethod
    def from_url(url, listing):
        if url.startswith('http'):
            return OldHTMLSolicitationReader.from_htmlurl(url, listing)
        else:
            return OldHTMLSolicitationReader.from_htmlfile(url, listing)

    @staticmethod
    def from_htmlfile(filename, listing=None):
        tree = html.parse(filename)
        return OldHTMLSolicitationReader(tree, listing)

    @staticmethod
    def from_htmlurl(url, listing=None):
        resp = requests.get(url)
        tree = html.fromstring(resp.content)
        return OldHTMLSolicitationReader(tree, listing)

    # blah.
    def get_solicitation_elems(self):
        xpath = "//p/b/span[contains(.,'Topic Descriptions')]/ancestor::p/following-sibling::*"
        elems = self.tree.xpath(xpath)
        if len(elems) == 0:
            xpath = "//p/b/span[contains(.,'Topic\nDescriptions')]/ancestor::p/following-sibling::*"
            elems = self.tree.xpath(xpath)
        if len(elems) == 0:
            xpath = "//p/b/span[contains(.,'TOPIC\nDESCRIPTIONS')]/ancestor::p/following-sibling::*"
            elems = self.tree.xpath(xpath)
        if len(elems) == 0:
            xpath = "//p/b/span[contains(.,'TOPIC DESCRIPTIONS')]/ancestor::p/following-sibling::*"
            elems = self.tree.xpath(xpath)
        if len(elems) == 0:
            xpath = "//h1[contains(.,'Topic Descriptions')]/following-sibling::*"
            elems = self.tree.xpath(xpath)
        if len(elems) == 0:
            xpath = "//p/span/b[contains(.,'Topic Descriptions')]/ancestor::p/following-sibling::*"
            elems = self.tree.xpath(xpath)
        if len(elems) == 0:
            xpath = "//h2/span[contains(.,'STTR TOPICS')]/ancestor::*/following-sibling::*"
            elems = self.tree.xpath(xpath)
        if len(elems) == 0:
            xpath = "//p/b/span[contains(.,'SBIR TOPICS')]/ancestor::*/following-sibling::*"
            elems = self.tree.xpath(xpath)
        if len(elems) == 0:
            xpath = "//p/b[contains(.,'STTR TOPIC DESCRIPTIONS')]/ancestor::*/following-sibling::*"
            elems = self.tree.xpath(xpath)

        return elems

    # this is so ugly
    @staticmethod
    def get_description(solicitation):

        desc_started = False
        desc_ended = False
        desc_strings = []
        for elem in solicitation:

            if not desc_ended:
                if elem.text_content().startswith(u"DESCRIPTION:"):
                    desc_strings.append(elem.text_content()[13:])
                    desc_started = True
                elif elem.text_content().startswith(u"REFERENCES:"):
                    desc_ended = True
                elif desc_started:
                    desc_strings.append(elem.text_content())
        desc_string = remove_newlines(u" ".join(desc_strings)).strip()
        desc_string = desc_string.replace(u'\xa0',u'')
        desc_string = re.sub(' +',' ',desc_string)
        desc_string = re.sub('\n',' ',desc_string)
        return desc_string

    # this is so ugly
    @staticmethod
    def get_references(solicitation):
        ref_started = False
        ref_strings = []
        for elem in solicitation:
            try:
                if elem.text_content().startswith(u"REFERENCES:"):
                    ref_started = True
                elif elem.text_content().startswith(u"KEYWORDS:"):
                    return ref_strings
                elif ref_started:
                    if not is_str_empty(elem.text_content()):
                        this_ref = (elem.text_content()).replace(u'\xa0', u'')
                        this_ref = re.sub('^[0-9]+\.\s', u'', this_ref)
                        ref_strings.append(this_ref.replace("\r\n"," "))
            except Exception as e:
                raise e
        # some days i hate unicode
        return ref_strings

    @staticmethod
    def process_solicitation(solicitation):
        sol = {}
        for elem in solicitation:

            if u"TITLE:" in elem.text_content():
                parts = elem.text_content().split(u"TITLE:")
                if parts[0].startswith(u"TOPIC:"):
                    topic_str = parts[0].split('TOPIC:')[1]
                    sol['topic'] = remove_newlines(topic_str).strip()
                else:
                    sol['topic'] = remove_nbsp(parts[0]).strip()
                sol['title'] = remove_newlines(" ".join(parts[1:]).strip())
            elif elem.text_content().startswith(u"OBJECTIVE:"):
                sol['objective'] = remove_newlines(elem.text_content()[11:]).strip()
            elif elem.text_content().startswith(u"TECHNOLOGY AREAS:"):
                tech_str = remove_newlines(elem.text_content()).strip()
                sol['tech_areas'] = process_tech_area_str(tech_str[18:])
            elif elem.text_content().startswith(u"KEYWORDS:"):
                keyw_str = remove_newlines(elem.text_content()).strip()
                sol['keywords'] = process_tech_area_str(keyw_str[10:])
        sol['description'] = OldHTMLSolicitationReader.get_description(solicitation)
        sol['references'] = OldHTMLSolicitationReader.get_references(solicitation)
        return sol

    @staticmethod
    def build_solicitations(elems):
        solicitations = []
        for elem in elems:
            new_solicit = OldHTMLSolicitationReader.process_solicitation(elem)
            if 'topic' in new_solicit:
                solicitations.append(new_solicit)
        return solicitations

    # Basically we just go through all the elements until we find a KEYWORDS: which means its at the end
    # Naturally this assumes KEYWORDS is mandatory and at the end. Is it? Who knows..
    @staticmethod
    def build_solicitations_raw(elems):
        solicitations = []
        clean_end = False
        this_solicitation = []
        for elem in elems:
            text_str = elem.text_content()
            if text_str.startswith(u"KEYWORDS:"): # end marker
                this_solicitation += elem
                clean_end = True # hack?
                solicitations.append(this_solicitation)
                this_solicitation = []  # zero out
            elif text_str.startswith(u"TOPIC:"): # we overshot
                solicitations.append(this_solicitation)
                this_solicitation = [elem] # prime next
            else:
                this_solicitation += elem
        if not clean_end:
            solicitations.append(this_solicitation)
        return solicitations


    def __getitem__(self, item):
        return self.solicitations[item]


    def __len__(self):
        return len(self.solicitations)


    def __iter__(self):
        return iter(self.solicitations)


    def merge_parent_listing_info(self, listing):
        for solicitation in self.solicitations:
            solicitation.update(listing)


class HTMLSolicitationReader(Sequence):
    def __init__(self, tree, listing=None):
        self.tree = tree
        self.elems = self.get_solicitation_elems()
        # could do this lazily but they're so small why bother...
        self.solicitations = self.make_solicitations()
        if listing:
            self.merge_parent_listing_info(listing)

    @staticmethod
    def from_url(url, listing):
        if url.startswith('http'):
            return HTMLSolicitationReader.from_htmlurl(url, listing)
        else:
            return HTMLSolicitationReader.from_htmlfile(url, listing)

    @staticmethod
    def from_htmlfile(filename, listing=None):
        tree = html.parse(filename)
        return HTMLSolicitationReader(tree, listing)

    @staticmethod
    def from_htmlstr(str):
        tree = html.fromstring(str)
        return HTMLSolicitationReader(tree)

    @staticmethod
    def from_htmlurl(url, listing=None):
        resp = requests.get(url)
        tree = html.fromstring(resp.content)
        return HTMLSolicitationReader(tree, listing)


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
    def get_techareas(elem):
        try:
            tech_areas = elem.xpath("p[starts-with(.,'TECHNOLOGY AREA')]")[0].text
            return process_tech_area_str(tech_areas[20:])
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

    def merge_parent_listing_info(self, listing):
        for solicitation in self.solicitations:
            solicitation.update(listing)




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
                    sol['tech_areas'] = process_tech_area_str(elem.xpath('div')[0].text)
                    sol['topic'] = "ERROR: Malformed Topic"
                    sol['title'] = "ERROR: Malformed Title"
                    broken_topic = True
                if not any(s in title for s in ["has been removed","has been deleted"]):
                    sol['references'] = self.get_references(elem)
                    sol['description'] = self.get_description(elem)
                    sol['keywords'] = self.get_keywords(elem)
                if not broken_topic:
                    if title.startswith("TITLE:"):
                        sol['title'] = title[7:]
                    else:
                        sol['title'] = title
                    sol['objective'] = self.get_objective(elem)
                    sol['tech_areas'] = self.get_techareas(elem)

                    solicitations.append(sol)
        return solicitations




