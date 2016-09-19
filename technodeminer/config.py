# CONFIG Settings
MIN_NGRAM_LENGTH = 2

# Data Location
SBIR_LOC = "/home/brian/technodeminer/data/sbir/sbirs.xlsx"

# Database Stuff
ARANGO_HOSTNAME = "localhost"
ARANGO_PORT = 8529
ARANGODB_NAME = "technodeminer"
GRAPH_NAME = "technode_graph"

# names of collections in the database (i.e. tables)
KEYPHRASE_COLLECTION = 'keyphrases'
CONTRACT_COLLECTION = 'contracts'
R2_COLLECTION = 'r2_exhibits'
SOLICITATION_COLLECTION = 'solicitations'

# relation collections
SOLICITATION_CONTRACT_RELATIONS = "solicitation_contract_relations"
KEYPHRASE_CONTRACT_RELATIONS = "keyphrase_contract_relations"
KEYPHRASE_R2_RELATIONS = "keyphrase_r2_relations"
KEYPHRASE_SOLICITATION_RELATIONS = "keyphrase_solicitation_relations"
