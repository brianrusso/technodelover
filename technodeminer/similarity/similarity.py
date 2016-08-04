from technodeminer.persistence.graph import connect_to_arango, get_technode_graph
from pattern.vector import Model, Document


db = connect_to_arango()
graph = get_technode_graph(db)
r2_exhibits = db.col('r2_exhibits')
solicitations = db.col('solicitations')


# for each solicitation
#for solicitation in solicitations.all():
# constrain to air force FY16
solicit_gen = solicitations.get_by_example({"Component": "Air Force", "Fiscal Year": "FY16"})
r2_queries = [{"byear": 2013, "agency": "Air Force", "ba_num": 1},
              {"byear": 2013, "agency": "Air Force", "ba_num": 2},
              {"byear": 2013, "agency": "Air Force", "ba_num": 3}]

# find all the contracts that use the same topic code
r2_list = []
for query in r2_queries:
    for r2 in r2_exhibits.get_by_example(query):
        try:
            strings = [r2['program_desc']]
            projects = [r2['projects'] for k in r2['projects'].keys()]
            for proj in projects:
                try:
                    strings.append(proj['mission_desc'])
                except KeyError as e:
                    pass
            doc = Document(" ".join(strings), name=r2['_id'])
            r2_list.append(doc)
        except KeyError as e:
            print repr(e) # not much to do about this
m = Model(r2_list)


#    for contract in related_contracts:
#        graph.create_edge("solicitation_contract_relations", {"_from": solicitation['_id'],
#                                                              "_to": contract['_id']})

