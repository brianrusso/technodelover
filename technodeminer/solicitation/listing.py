from collections import Sequence
import copy
import requests
from lxml import etree
import urlparse
from technodeminer.solicitation.model import HTMLSolicitationReader, OldHTMLSolicitationReader
import time

class SolicitationFormatNotSupportedException(Exception):
    def __init__(self, type):
        pass

PAST_SOLICITATIONS = "http://www.acq.osd.mil/osbp/sbir/solicitations/archives.shtml"
PAST_ROOT = "http://www.acq.osd.mil/osbp/sbir/solicitations/"  # this might break
TP_TABLE_XPATH = '//*[@id="mainCol"]/table'
TP_TABLE_OFFSET = 1
DESIRABLE_TP_TABLE_COLUMN_NUMBER = 3
#AGENCY_TABLE_XPATH = '//*[@id="mainCol"]/table'
AGENCY_TABLE_XPATH = '//*/table[@cellpadding=0]'
AGENCY_TABLE_OFFSET = 2 # how many to skip, 1st 3 are headers/blank/instructions we don't care about... EXCEPT in some.. blah
AGENCY_TABLE_MIN_NUM_COLUMNS = 3
ANTI_LEECH_IN_SECONDS = 3


def listing_to_graph(listing, graph, db):
    #time.sleep(ANTI_LEECH_IN_SECONDS)
    contracts = db.col('contracts')
    try:
        reader = AgencyReader.get_solicitationreader(listing)
        if (len(reader) <1) and ("preface" not in listing['ComponentURL']):
                raise Exception("Length <0; probable parser error")

        for solicitation in reader:
            if solicitation['title']:
                resp = graph.create_vertex("solicitations", solicitation)
                if solicitation['topic']:
                    related_contracts = contracts.get_by_example({'topic_code': solicitation['topic']})
                    for contract in related_contracts:
                        graph.create_edge("solicitation_contract_relations", {"_from": resp['_id'],
                                            "_to": contract['_id'],
                                            "topic_code": solicitation['topic']})
    except SolicitationFormatNotSupportedException:
        pass

class ListingReader(Sequence):
    def __init__(self, past_solicits_url=PAST_SOLICITATIONS):
        self.tree = self.get_listing_tree(past_solicits_url)
        self.tplistings = self.get_tp_listings()

    def get_listing_tree(self,past_solicits_url):
        resp = requests.get(past_solicits_url)
        tree = etree.HTML(resp.content)
        return tree

    def __getitem__(self, item):
        return self.tplistings[item]

    def __len__(self):
        return len(self.tplistings)

    def __iter__(self):
        return iter(self.tplistings)

    # first elem is header (th), some may be empty. Considered empty if 2nd column [1] is empty.
    # FRAGILE
    def get_tp_listings(self):
        listings = []
        table = self.tree.xpath(TP_TABLE_XPATH)[0]
        elems = table.findall('tr')
        headers = [elem.text for elem in (elems[0].findall('th'))]
        running_fy = None
        for row in elems[TP_TABLE_OFFSET:]:
            cols = row.findall('td')
            if len(cols) == DESIRABLE_TP_TABLE_COLUMN_NUMBER: # normally prefer to do try/except, but this is more readable here.
                this_solicit = {}
                # get FY
                try:
                    fy = cols[0].find('span').text
                    running_fy = fy # update if we get a new FY
                except AttributeError:
                    fy = running_fy # no FY, default to running one.

                this_solicit[headers[0]] = fy
                this_solicit[headers[1]] = urlparse.urljoin(PAST_ROOT, cols[1].find('a').attrib['href'])
                this_solicit[headers[2]] = cols[2].text
                listings.append(this_solicit)
        return listings

    def get_agency_listings(self, tplisting):
        return AgencyReader(tplisting)

    def get_all_agency_listings(self):
        listings = []
        for tp_listing in self:
            time.sleep(2)
            listings += [agency_listing for agency_listing in AgencyReader(tp_listing)]
        return listings


class AgencyReader(Sequence):
    def __init__(self, tplisting):
        self.s = requests.Session()
        a = requests.adapters.HTTPAdapter(max_retries=5)
        self.s.mount('http://', a)
        self.tplisting = tplisting
        self.tree = self.get_agency_tree(tplisting)
        self.agency_listings = self.get_agency_listings_for_tp()

    def get_agency_tree(self, timeperiod_listing):
        time.sleep(ANTI_LEECH_IN_SECONDS)
        resp = self.s.get(timeperiod_listing['Solicitation'])
        tree = etree.HTML(resp.content)
        return tree

    def __getitem__(self, item):
        return self.agency_listings[item]

    def __len__(self):
        return len(self.agency_listings)

    def __iter__(self):
        return iter(self.agency_listings)

    @staticmethod
    def get_best_doc_type(cols, base_url):
        urls = []
        for col in cols[2:]:
            try:
                urls.append(col.find('a').attrib['href'])
            except AttributeError:
                pass
        htm_str = next((s for s in urls if s.endswith('.htm')), None)
        html_str = next((s for s in urls if s.endswith('.html')), None)
        pdf_str = next((s for s in urls if s.endswith('.pdf')), None)
        doc_str = next((s for s in urls if s.endswith('.doc')), None)

        if htm_str:
            doc_type = "HTM"
            output_str = htm_str
        elif html_str:
            doc_type = "HTML"
            output_str = html_str
        elif pdf_str:
            doc_type = "PDF"
            output_str = pdf_str
        elif doc_str:
            doc_type = "Doc"
            output_str = doc_str
        else:
            doc_type = None
            output_str = ""

        if doc_type:
            output_url = urlparse.urljoin((base_url + "/"), output_str)
        else:
            output_url = ""
        return (doc_type, output_url)

    def get_agency_listings_for_tp(self):
        these_agency_listings = []
        tree = self.get_agency_tree(self.tplisting)
        base_url = self.tplisting["Solicitation"].rsplit('/', 1)[0]
        tables = tree.xpath(AGENCY_TABLE_XPATH)

        for table in tables:
            elems = table.findall('tr')
            for row in elems[AGENCY_TABLE_OFFSET:]:
                cols = row.findall('td')
                component_txt = cols[0].find('strong').text
                # always something.. this format sucks
                if "Instructions" not in component_txt:
                    if len(cols) >= AGENCY_TABLE_MIN_NUM_COLUMNS:
                        this_agency_listing = copy.deepcopy(self.tplisting)
                        this_agency_listing["Component"] = component_txt
                        doc_type, doc_url = self.get_best_doc_type(cols, base_url)
                        if doc_type:
                            this_agency_listing["DocType"] = doc_type
                            this_agency_listing["ComponentURL"] = doc_url
                            these_agency_listings.append(this_agency_listing)
                    else:
                        print "insufficent columns %d" % (len(cols))
                        print self.tplisting
        return these_agency_listings


    def get_solicitations(self):
        solicitations = []
        for listing in self:
            solicitations.append(self.get_solicitationreader(listing))
        return solicitations

    @staticmethod
    def get_solicitationreader(listing):
        if listing['DocType'] == "HTML":
            try:
                return HTMLSolicitationReader.from_url(listing['ComponentURL'], listing)
            except Exception as e:
                print "ERROR: %s" % repr(e)

        elif listing['DocType'] == "HTM":
            try:
                return OldHTMLSolicitationReader.from_url(listing['ComponentURL'], listing)
            except Exception as e:
                print "ERROR: %s" % repr(e)
        else:
            raise SolicitationFormatNotSupportedException("PDF")
            # don't care about this right now
            #raise Exception("%s listing type not supported" % (listing['DocType']))

