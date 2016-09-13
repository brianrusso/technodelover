import requests
from collections import Sequence
from lxml import html
from technodeminer.util import nonelessdict, remove_nbsp, remove_newlines, is_str_empty
import re

def process_tech_area_str(str):
    if ";" in str:
        DELIMITER = ";"
    else:
        DELIMITER = ","
    tech_areas = str.split(DELIMITER)
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

    # blah. This could probably be refactored.
    def get_solicitation_elems(self):  # p/b/span/Topic Descriptions
        xpath = "//p/b/span[contains(normalize-space(.),'Topic Descriptions')]/ancestor::p/following-sibling::*"
        elems = self.tree.xpath(xpath)
        if len(elems) == 0: # p/b/span Topic\nDescriptions
            xpath = "//h2[contains(normalize-space(.),'Topic Descriptions')]/ancestor::p/following-sibling::*"
            elems = self.tree.xpath(xpath)
        if len(elems) == 0: # p/b/span Topic\nDescriptions
            xpath = "//p/b/span[contains(.,'Topic\nDescriptions')]/ancestor::p/following-sibling::*"
            elems = self.tree.xpath(xpath)
        if len(elems) == 0: # p/strong/span Topic Descriptions
            xpath = "//p/strong/span[contains(normalize-space(.),'Topic Descriptions')]/ancestor::p/following-sibling::*"
            elems = self.tree.xpath(xpath)
        if len(elems) == 0: # p/b/span Topic\nDescriptions
            xpath = "//p/b/span[contains(.,'Topic\r\nDescriptions')]/ancestor::p/following-sibling::*"
            elems = self.tree.xpath(xpath)
        if len(elems) == 0: # p/b/span/ + caps + nl
            xpath = "//p/b/span[contains(.,'TOPIC\nDESCRIPTIONS')]/ancestor::p/following-sibling::*"
            elems = self.tree.xpath(xpath)
        if len(elems) == 0: # p/b/span + caps
            xpath = "//p/b/span[contains(.,'TOPIC DESCRIPTIONS')]/ancestor::p/following-sibling::*"
            elems = self.tree.xpath(xpath)
        if len(elems) == 0: # h1 + regular case
            xpath = "//h1[contains(.,'Topic Descriptions')]/following-sibling::*"
            elems = self.tree.xpath(xpath)
        if len(elems) == 0: # p/span/b + regular case
            xpath = "//p/span/b[contains(.,'Topic Descriptions')]/ancestor::p/following-sibling::*"
            elems = self.tree.xpath(xpath)
        if len(elems) == 0: # h2/span + caps sttr
            xpath = "//h2/span[contains(.,'STTR TOPICS')]/ancestor::*/following-sibling::*"
            elems = self.tree.xpath(xpath)
        if len(elems) == 0: # h3/span + sttr
            xpath = "//h3/span[contains(.,'STTR TOPIC DESCRIPTIONS')]/ancestor::*/following-sibling::*"
            elems = self.tree.xpath(xpath)
        if len(elems) == 0: # p/b/span + caps sbir
            xpath = "//p/b/span[contains(.,'SBIR TOPICS')]/ancestor::*/following-sibling::*"
            elems = self.tree.xpath(xpath)
        if len(elems) == 0: # p/b + caps sttr
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
#        xpath = "//div[preceding-sibling::comment()[. = ' begin-topic-desc ']]" \
#                "[following-sibling::comment()[. = ' end-topic-desc ']]"
        xpath = "//div[preceding-sibling::comment()[contains(.,'begin-topic-desc')]]"
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
            KEYWORD_DELIMITER = ","
            if ";" in keywords_str:
                KEYWORD_DELIMITER = ";"
            for kw in keywords_str[10:].split(KEYWORD_DELIMITER): keywords.append(kw.strip())
            return keywords
        except IndexError:
            return None

    def merge_parent_listing_info(self, listing):
        for solicitation in self.solicitations:
            solicitation.update(listing)

    @staticmethod
    def strip_title(title):
        if title.startswith("TITLE:"):
            return title[7:].strip()
        else:
            return title.strip()


    def make_solicitations(self):
        broken_topic = False  # Not really a fan of this.. will refactor if we find more

        solicitations = list()
        for elem in self.elems:
            title = None
            sol = nonelessdict()
            if len(elem.xpath('div')) > 0:
                sol['topic'] = elem.xpath('div')[0].text_content()
                title = elem.xpath('div')[1].text_content()
            elif len(elem.xpath('table/tr/td')) >0:  # try the table version, e.g. darpa153-dp2.html
                sol['topic'] = elem.xpath('table/tr/td')[0].text_content().strip()
                title = elem.xpath('table/tr/td')[1].text_content().strip()
#                if title.startswith("OBJECTIVE"): # some are messed up like this, e.g. af161
#                    sol['objective'] = title
#                    sol['tech_areas'] = process_tech_area_str(elem.xpath('div')[0].text)
#                    sol['topic'] = "ERROR: Malformed Topic"
#                    sol['title'] = "ERROR: Malformed Title"
#                    broken_topic = True
            if title:
                if any(s in title for s in ["has been removed", "has been deleted"]):
                    pass
                else:
                    sol['references'] = self.get_references(elem)
                    sol['description'] = self.get_description(elem)
                    sol['keywords'] = self.get_keywords(elem)
                    sol['title'] = self.strip_title(title)
                    sol['objective'] = self.get_objective(elem)
                    sol['tech_areas'] = self.get_techareas(elem)
                    solicitations.append(sol)


        return solicitations




