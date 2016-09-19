from arango import Arango
from technodeminer.config import *



def connect_to_arango():
    a = Arango(host=ARANGO_HOSTNAME, port=ARANGO_PORT, username='root', password='joker')
    try:
        user_info = dict()
        user_info['username'] = 'root'
        user_info['passwd'] = 'joker'
        user_info['active'] = True
        db = a.create_database(ARANGODB_NAME, users=[user_info])
        return db
    except:
        db = a.database(ARANGODB_NAME)
        return db

def get_technode_graph(db):
    try:
        graph = db.create_graph(GRAPH_NAME)
    except:
        graph = db.graph(GRAPH_NAME)
    return graph

def build_collections():
    db = connect_to_arango()
    graph = get_technode_graph(db)

    for collection in [R2_COLLECTION, CONTRACT_COLLECTION, SOLICITATION_COLLECTION, KEYPHRASE_COLLECTION]:
        try:
            db.create_collection(collection)
            graph.create_vertex_collection(collection)
        except Exception as e:
            print repr(e)
    # relation between solicitation and contract (explicit, based on topic code)
    try:
        db.create_collection(SOLICITATION_CONTRACT_RELATIONS, is_edge=True)
        graph.create_edge_definition(edge_collection=SOLICITATION_CONTRACT_RELATIONS,
                                     from_vertex_collections=[SOLICITATION_COLLECTION],
                                     to_vertex_collections=[CONTRACT_COLLECTION])
    except Exception as e:
        print repr(e)

    # relation between terms and r2s
    try:
        db.create_collection(KEYPHRASE_R2_RELATIONS, is_edge=True)
        graph.create_edge_definition(edge_collection=KEYPHRASE_R2_RELATIONS,
                                     from_vertex_collections=[KEYPHRASE_COLLECTION],
                                     to_vertex_collections=[R2_COLLECTION])
    except Exception as e:
        print repr(e)

    # relation between terms and solicitations
    try:
        db.create_collection(KEYPHRASE_SOLICITATION_RELATIONS, is_edge=True)
        graph.create_edge_definition(edge_collection=KEYPHRASE_SOLICITATION_RELATIONS,
                                     from_vertex_collections=[KEYPHRASE_COLLECTION],
                                     to_vertex_collections=[SOLICITATION_COLLECTION])
    except Exception as e:
        print repr(e)

    # relation between terms and contracts
    try:
        db.create_collection(KEYPHRASE_CONTRACT_RELATIONS, is_edge=True)
        graph.create_edge_definition(edge_collection=KEYPHRASE_CONTRACT_RELATIONS,
                                     from_vertex_collections=[KEYPHRASE_COLLECTION],
                                     to_vertex_collections=[CONTRACT_COLLECTION])
    except Exception as e:
        print repr(e)
    return graph

