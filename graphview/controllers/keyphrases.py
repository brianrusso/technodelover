from flask import Blueprint, render_template, flash, request, redirect, url_for
from graphview.models import db
from json import loads, dumps
import networkx as nx
from networkx.readwrite import json_graph
import farmhash

keyphrases = Blueprint('keyphrases', __name__)

def get_keyphrasecoll():
    coll = db.collection("keyphrases")
    return coll

@keyphrases.route('/')
def home():
    return render_template('index.html')

# Mmm hash-browns!
def get_hash_for_key(key):
    return str(farmhash.hash64(key.encode('ascii','ignore')))

@keyphrases.route('/keyphrases')
def list_authors():
    return dumps(get_keyphrasecoll().first(5))


@keyphrases.route('/v1/<key>.json')
def get_author(key):
    return dumps(get_keyphrasecoll().document(get_hash_for_key(key)))

@keyphrases.route('/v1/<key>-execute.json')
def get_authorx(key):
    return dumps(_get_keyphrase_neighbors("keyphrases/"+(get_hash_for_key(key))))


@keyphrases.route('/v1/<collection>/<key>/<distance>-neighbors.json')
def get_author_neighbors(key, collection, distance):
    return dumps(list(_get_variable_neighborhood(collection+"/"+get_hash_for_key(key), int(distance))))


@keyphrases.route('/v1/<collection>/<key>/<distance>-graph.json')
def get_author_neighbors_nx(key, collection, distance):
    return dumps(json_graph.node_link_data(_get_variable_neighborhood_as_nx(collection+"/"+get_hash_for_key(key), int(distance))))

@keyphrases.route('/v1/<collection>/<key>/<distance>-3dgraph.json')
def get_author_neighbors_nx_3d(key, collection, distance):
    nxgraph = _get_variable_neighborhood_as_nx(collection+"/"+get_hash_for_key(key), int(distance))
    nx_3dgraph = nxgraph_to_graphosaurus(nxgraph)
    return nx_3dgraph

def nxgraph_to_graphosaurus(nxgraph):
    output = {}
    output["vertices"] = make_vertices_for_3dlayout(nxgraph)
    output["edges"] = edge_tuples_to_array(nxgraph)
    return dumps(output)

# vertices for graphosaurus
def make_vertices_for_3dlayout(nxgraph):
    nx_3dlayout = nx.layout.spring_layout(nxgraph, dim=3)
    # need to create an array of arrays where last 3 are xyz, first is key
    output = []
    for k,v in nx_3dlayout.iteritems():
        this_elem = [k] + v.tolist()
        output.append(this_elem)
    return output

# edges for graphosaurus
# need to convert array of tuples into array of arrays
def edge_tuples_to_array(nxgraph):
    output = [[elem[0]] + [elem[1]] for elem in nxgraph.edges()]
    return output

@keyphrases.route('/graphosaurus.html')
def graphosaurus():
    key = "contracts/375757258483"
    distance = 1
    return render_template('keyphrases/graphosaurus.html', key=key, distance=int(distance))

@keyphrases.route('/v1/keyphrases/<key>/<distance>-graph.html')
def get_author_neighbors_nx_force(key, distance):
    return render_template('keyphrases/node_forcegraph.html', key=key, distance=int(distance))


def _get_keyphrase_neighbors(key):
    cursor = db.execute_query(
        "FOR V IN ANY @val GRAPH \"technode_graph\" RETURN V._id",
        bind_vars={"val": key}
    )
    neighbors = []
    for doc in cursor:
        neighbors.append(doc)
    return neighbors

def _get_variable_neighborhood(key, distance):
    if distance <= 0:
        raise Exception("Distance must be >= 1")
    elif distance == 1:
        return set(_get_keyphrase_neighbors(key))
    else:
        results = set(_get_keyphrase_neighbors(key))
        for neighbor in _get_keyphrase_neighbors(key):
            new_set = _get_variable_neighborhood(neighbor, distance-1)
            results = results.union(new_set)
        return results

def _get_variable_neighborhood_as_nx(key, distance):
    g = nx.Graph()
    if distance <= 0:
        raise Exception("Distance must be >= 1")
    elif distance == 1:
        results = set(_get_keyphrase_neighbors(key))
        for neighbor in results:
            g.add_node(neighbor)
            g.add_edge(neighbor, key)
        return g
    else:
        results = set(_get_keyphrase_neighbors(key))
        # prime with immediate neighbors
        for neighbor in results:
            g.add_node(neighbor)
            g.add_edge(neighbor, key)
        # recurse to neighbors
        for neighbor in results:
            new_set = _get_variable_neighborhood(neighbor, distance-1)
            for their_neighbor in new_set:
                g.add_node(their_neighbor)
                g.add_edge(their_neighbor, neighbor)
            results = results.union(new_set)
        return g
