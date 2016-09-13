
from arango import Arango

a = Arango(host="localhost", port=8529, username='root', password='joker')
db = a.database("technodeminer")
