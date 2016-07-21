import copy
import requests
from lxml import etree
import urlparse
from model import HTMLSolicitationReader


PAST_SOLICITATIONS = "http://www.acq.osd.mil/osbp/sbir/solicitations/archives.shtml"
PAST_ROOT = "http://www.acq.osd.mil/osbp/sbir/solicitations/"  # this might break
TP_TABLE_XPATH = '//*[@id="mainCol"]/table'
TP_TABLE_OFFSET = 1
DESIRABLE_TP_TABLE_COLUMN_NUMBER = 3
#AGENCY_TABLE_XPATH = '//*[@id="mainCol"]/table'
AGENCY_TABLE_XPATH = '//*/table[@cellpadding=0]'
AGENCY_TABLE_OFFSET = 2 # how many to skip, 1st 3 are headers/blank/instructions we don't care about... EXCEPT in some.. blah
AGENCY_TABLE_MIN_NUM_COLUMNS = 3

def get_listing_tree(url=PAST_SOLICITATIONS):
    resp = requests.get(url)
    tree = etree.HTML(resp.content)
    return tree

def get_agency_tree(timeperiod_listing):
    print timeperiod_listing['Solicitation']
    resp = requests.get(timeperiod_listing['Solicitation'])
    tree = etree.HTML(resp.content)
    return tree

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
        doc_type = "HTML"
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


def get_agency_listings_for_tp(timeperiod_listing):
    these_agency_listings = []
    tree = get_agency_tree(timeperiod_listing)
    base_url = timeperiod_listing["Solicitation"].rsplit('/',1)[0]
    tables = tree.xpath(AGENCY_TABLE_XPATH)

    for table in tables:
        elems = table.findall('tr')

        for row in elems[AGENCY_TABLE_OFFSET:]:
            cols = row.findall('td')
            component_txt = cols[0].find('strong').text
            # always something.. this format sucks
            if "Instructions" not in component_txt:
                if len(cols) >= AGENCY_TABLE_MIN_NUM_COLUMNS:
                    this_agency_listing = copy.deepcopy(timeperiod_listing)
                    this_agency_listing["Component"] = component_txt
                    doc_type, doc_url = get_best_doc_type(cols, base_url)
                    if doc_type:
                        this_agency_listing["DocType"] = doc_type
                        this_agency_listing["ComponentURL"] = doc_url
                        these_agency_listings.append(this_agency_listing)
                else:
                    print "insufficent columns %d" % (len(cols))
                    print timeperiod_listing
    return these_agency_listings

# first elem is header (th), some may be empty. Considered empty if 2nd column [1] is empty.
# FRAGILE
def get_tp_solicitation_listings(tree):
    listings = []
    table = tree.xpath(TP_TABLE_XPATH)[0]
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

def get_solicitation_listings_by_agency(tp_solicitation_listings):
    full_listing = []
    for listing in tp_solicitation_listings:
        agency_listings = get_agency_listings_for_tp(listing)
        full_listing += agency_listings
    return full_listing

def build_listings():
    tree = get_listing_tree()
    tp_solicitation_listings = get_tp_solicitation_listings(tree)
    all_listings = get_solicitation_listings_by_agency(tp_solicitation_listings)
    return all_listings

def process_listings(listings):
    output_solicitations = []
    for listing in listings:
        if listing['DocType'] == "HTML":
            reader = SolicitationReader.from_htmlurl(listing['ComponentURL'])
            print "Processed %s, got %d solicitations" % (listing['ComponentURL'], len(reader))
            output_solicitations += reader.solicitations
    return output_solicitations


if __name__ == '__main__':

    listings = build_listings()
    solicitations = process_listings(listings)
