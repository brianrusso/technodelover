from technodeminer.persistence.graph import connect_to_arango

def get_term_collection():
    db = connect_to_arango()
    return db.col('tech_terms')
