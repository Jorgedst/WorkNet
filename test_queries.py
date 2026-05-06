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

import time

with driver.session(database="005fc815") as s:
    
    t = time.time()
    r1 = s.run("MATCH (u:Usuario) RETURN u.email AS id, u.nombre AS label").data()
    print(f"Usuarios: {len(r1)} — {round(time.time()-t, 2)}s")

    t = time.time()
    r2 = s.run("MATCH (e:Empresa) RETURN e.nombre AS id").data()
    print(f"Empresas: {len(r2)} — {round(time.time()-t, 2)}s")

    t = time.time()
    r3 = s.run("MATCH (p:Proyecto) RETURN p.nombre AS id").data()
    print(f"Proyectos: {len(r3)} — {round(time.time()-t, 2)}s")

    t = time.time()
    r4 = s.run("MATCH (a:Usuario)-[:CONECTA_CON]->(b:Usuario) RETURN a.email AS from, b.email AS to").data()
    print(f"Conexiones: {len(r4)} — {round(time.time()-t, 2)}s")

    t = time.time()
    r5 = s.run("MATCH (u:Usuario)-[:TRABAJA_EN]->(e:Empresa) RETURN u.email AS from, e.nombre AS to").data()
    print(f"Trabaja en: {len(r5)} — {round(time.time()-t, 2)}s")

    t = time.time()
    r6 = s.run("MATCH (u:Usuario)-[:PARTICIPA_EN]->(p:Proyecto) RETURN u.email AS from, p.nombre AS to").data()
    print(f"Participa en: {len(r6)} — {round(time.time()-t, 2)}s")
driver.close()
