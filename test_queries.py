from neo4j import GraphDatabase
from services.graph_queries import *

URI  = "neo4j+s://005fc815.databases.neo4j.io"
AUTH = ("005fc815", "AU2Eg4WYv695j3VX6Byf1xamoIUruS5vsMRBwOoc5WM")

driver = GraphDatabase.driver(URI, auth=AUTH)

from neo4j import GraphDatabase
from services.graph_queries import *

URI  = "neo4j+s://005fc815.databases.neo4j.io"
AUTH = ("005fc815", "AU2Eg4WYv695j3VX6Byf1xamoIUruS5vsMRBwOoc5WM")

driver = GraphDatabase.driver(URI, auth=AUTH)

with driver.session(database="005fc815") as s:
    s.run("""
    MATCH (u:Usuario)
    WHERE u.password IS NULL
    SET u.password = 'worknet123'
    """)
    print("Passwords asignadas.")

driver.close()
