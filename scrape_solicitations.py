import copy
import requests
from lxml import etree
import urlparse
from technodeminer.solicitation.model import HTMLSolicitationReader, OldHTMLSolicitationReader
from technodeminer.persistence.graph import connect_to_arango, get_technode_graph
from technodeminer.solicitation.listing import ListingReader, AgencyReader, listing_to_graph
from redis import Redis
from rq import Queue
import time
import json

def associate_solicitation_contract():
    db = connect_to_arango()
    graph = get_technode_graph(db)
    contracts = db.col('contracts')
    solicitations = db.col('solicitations')

    # for each solicitation
    for solicitation in solicitations.all():
        # find all the contracts that use the same topic code
        related_contracts = contracts.get_by_example({'topic_code':solicitation['topic']})
        time.sleep(0.1)
        for contract in related_contracts:
            graph.create_edge("solicitation_contract_relations", {"_from": solicitation['_id'],
                                                                  "_to": contract['_id']})


def load_listings_from_file(filename):
    with open(filename,'r') as fd:
        return json.load(fd)

def get_listings_from_web():
    return ListingReader()

if __name__ == '__main__':
    q= Queue(connection=Redis())
    db = connect_to_arango()
    graph = get_technode_graph(db)
    if True:
        print "Building list of listings"
        listings = load_listings_from_file('/home/brian/technodeminer/local_listings.json')
        print "Getting agency listings"
        for listing in listings:
            print "Adding %s to job q" % (listing['ComponentURL'])
            q.enqueue(listing_to_graph, listing, graph, db)
    # run association
    else:
        associate_solicitation_contract()
