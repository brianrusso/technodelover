import copy
import requests
from lxml import etree
import urlparse
from technodeminer.solicitation.model import HTMLSolicitationReader, OldHTMLSolicitationReader
from technodeminer.persistence.graph import connect_to_arango, get_technode_graph, build_collections
from technodeminer.solicitation.listing import ListingReader, AgencyReader, listing_to_graph
SBIR_LOC = "/home/brian/technodeminer/data/sbir/sbirs.xlsx"
from technodeminer.sbir import SBIRReader
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

def load_sbir_contracts(graph):
    # init sbir's
    print "Loading XLS"
    reader = SBIRReader(SBIR_LOC)
    print "Loading contracts into arango"
    for contract in reader:
        graph.create_vertex("contracts", contract)



def get_listings_from_web():
    return ListingReader()

if __name__ == '__main__':
    sque = Queue('solicitation_load', connection=Redis())
    db = connect_to_arango()
    build_collections()
    graph = get_technode_graph(db)
    # Load SBIR Contracts before Solicitations
    #load_sbir_contracts(graph)
    print "Building list of listings"
    listings = load_listings_from_file('/home/brian/technodeminer/local_listings.json')
    print "Enqueing solicitation load tasks"
    for listing in listings:
        print "Adding %s to job q" % (listing['ComponentURL'])
        sque.enqueue(listing_to_graph, listing, graph, db)
