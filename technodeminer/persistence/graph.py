from arango import Arango

ARANGODB_NAME = "technodeminer"
SBIR_LOC = "/home/brian/technodeminer/data/sbir/sbirs.xlsx"

def connect_to_arango():

    a = Arango(host="localhost", port=8529, username='root', password='joker')
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
        graph = db.create_graph("technode_graph")
    except:
        graph = db.graph("technode_graph")
    return graph

def build_collections():
    db = connect_to_arango()
    graph = get_technode_graph(db)

    try:
        db.create_collection("r2_exhibits")
        graph.create_vertex_collection("r2_exhibits")
        db.create_collection("contracts")
        graph.create_vertex_collection("contracts")
        db.create_collection("r2_contract_relations", is_edge=True)
        graph.create_edge_definition(edge_collection="r2_contract_relations",
                                     from_vertex_collections=["r2_exhibits"],
                                     to_vertex_collections=["contracts"])
    except Exception as e:
        print repr(e)
    try:
        db.create_collection("solicitations")
        graph.create_vertex_collection("solicitations")
        db.create_collection("solicitation_contract_relations", is_edge=True)
        graph.create_edge_definition(edge_collection="solicitation_contract_relations",
                                     from_vertex_collections=["solicitations"],
                                     to_vertex_collections=["contracts"])
    except Exception as e:
        print repr(e)
    return graph

