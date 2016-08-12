from technodeminer.persistence.graph import connect_to_arango, get_technode_graph, build_collections
from technodeminer.solicitation.listing import ListingReader, listing_to_graph
SBIR_LOC = "/home/brian/technodeminer/data/sbir/sbirs.xlsx"
R2_LOC = "/media/sf_Data/CTV_R2"
from technodeminer.sbir import SBIRReader
import time
import json
from technodeminer.r2.model import r2file_to_arango
from technodeminer.r2.util import get_filenames
from redis import Redis
from rq import Queue


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
    reader = SBIRReader(SBIR_LOC)
    for contract in reader:
        graph.create_vertex("contracts", contract)

def load_r2_exhibits():
    r2_files = get_filenames(R2_LOC)

    q = Queue('r2_load', connection=Redis())
    for file in r2_files:
        if file.lower().endswith(".xml"):
            q.enqueue(r2file_to_arango, file)
            #print "Loading %s" % (file)

def load_solicitation_listings():
    sque = Queue('solicitation_load', connection=Redis())
    listings = load_listings_from_file('/home/brian/technodeminer/local_listings.json')
    print "Enqueing solicitation load tasks"
    for listing in listings:
        #print "Adding %s to job q" % (listing['ComponentURL'])
        sque.enqueue(listing_to_graph, listing, graph, db)


def get_listings_from_web():
    return ListingReader()

if __name__ == '__main__':
    db = connect_to_arango()
    build_collections()
    graph = get_technode_graph(db)
    # Load SBIR Contracts before Solicitations
    print "Loading contracts"
    load_sbir_contracts(graph)
    print "Enqueuing solicitation jobs"
    load_solicitation_listings()
    print "Enqueuing r2 jobs"
    load_r2_exhibits()
