from neo4j import GraphDatabase

URI = "neo4j+s://005fc815.databases.neo4j.io"
AUTH = ("005fc815", "AU2Eg4WYv695j3VX6Byf1xamoIUruS5vsMRBwOoc5WM")

# ── Driver singleton ──────────────────────────────────────────────────────────
_driver = None

def get_driver():
    """Retorna la instancia singleton del driver Neo4j.
    
    Usar esta función en lugar de crear el driver directamente,
    así se reutiliza la misma conexión en todo el proyecto.
    """
    global _driver
    if _driver is None:
        _driver = GraphDatabase.driver(URI, auth=AUTH)
    return _driver


### NODOS ###

def crear_usuario(driver, email, nombre, cargo, ciudad):
    driver.execute_query(
        """
        MERGE (u:Usuario {email: $email})
        SET u.nombre = $nombre, 
            u.cargo = $cargo, 
            u.ciudad = $ciudad
        """,
        email=email, nombre=nombre, cargo=cargo, ciudad=ciudad,
        database_="005fc815",
    )

def crear_proyecto(driver, descripcion, nombre, tecnologias):
    driver.execute_query(
        """
        MERGE (p:Proyecto {nombre: $nombre})
        SET p.descripcion = $descripcion, 
            p.tecnologias = $tecnologias
        """,
        nombre=nombre, descripcion=descripcion, tecnologias=tecnologias,
        database_="005fc815",
    )

def crear_oferta(driver, titulo, salario, modalidad):
    driver.execute_query(
        """
        MERGE (o:Oferta {titulo: $titulo})
        SET o.salario = $salario, 
            o.modalidad = $modalidad
        """,
        titulo=titulo, salario=salario, modalidad=modalidad,
        database_="005fc815",
    )

def crear_habilidad(driver, nombre, categoria):
    driver.execute_query(
        """
        MERGE (h:Habilidad {nombre: $nombre})
        SET h.categoria = $categoria
        """,
        nombre=nombre, categoria=categoria,
        database_="005fc815",
    )

def crear_empresa(driver, nombre, ciudad, sector):
    driver.execute_query(
        """
        MERGE (e:Empresa {nombre: $nombre})
        SET e.ciudad = $ciudad,
            e.sector = $sector
        """,
        nombre=nombre, ciudad=ciudad, sector=sector,
        database_="005fc815",
    )


### RELACIONES ###

def conecta_con(driver, email1, email2):
    driver.execute_query(
        """
        MATCH (a:Usuario {email: $email1})
        MATCH (b:Usuario {email: $email2})
        MERGE (a)-[:CONECTA_CON]->(b)
        """,
        email1=email1, email2=email2,
        database_="005fc815",
    )

def trabaja_en(driver, email_usuario, nombre_empresa):
    driver.execute_query(
        """
        MATCH (u:Usuario {email: $email})
        MATCH (e:Empresa {nombre: $empresa})
        MERGE (u)-[:TRABAJA_EN]->(e)
        """,
        email=email_usuario, empresa=nombre_empresa,
        database_="005fc815",
    )

def tiene_habilidad(driver, email_usuario, nombre_habilidad):
    driver.execute_query(
        """
        MATCH (u:Usuario {email: $email})
        MATCH (h:Habilidad {nombre: $habilidad})
        MERGE (u)-[:TIENE_HABILIDAD]->(h)
        """,
        email=email_usuario, habilidad=nombre_habilidad,
        database_="005fc815",
    )

def participa_en(driver, email_usuario, nombre_proyecto):
    driver.execute_query(
        """
        MATCH (u:Usuario {email: $email})
        MATCH (p:Proyecto {nombre: $proyecto})
        MERGE (u)-[:PARTICIPA_EN]->(p)
        """,
        email=email_usuario, proyecto=nombre_proyecto,
        database_="005fc815",
    )

def publica_oferta(driver, nombre_empresa, titulo_oferta):
    driver.execute_query(
        """
        MATCH (e:Empresa {nombre: $empresa})
        MATCH (o:Oferta {titulo: $oferta})
        MERGE (e)-[:PUBLICA]->(o)
        """,
        empresa=nombre_empresa, oferta=titulo_oferta,
        database_="005fc815",
    )

def requiere_habilidad(driver, titulo_oferta, nombre_habilidad):
    driver.execute_query(
        """
        MATCH (o:Oferta {titulo: $oferta})
        MATCH (h:Habilidad {nombre: $habilidad})
        MERGE (o)-[:REQUIERE]->(h)
        """,
        oferta=titulo_oferta, habilidad=nombre_habilidad,
        database_="005fc815",
    )


# ── Script de carga inicial (ejecutar directamente, no al importar) ───────────
if __name__ == "__main__":
    driver = get_driver()

    ### CREAR NODOS ###
    crear_usuario(driver, "ruiz@gmail.com", "Arnulfo Ruiz", "Desarrollador", "Barranquilla")
    crear_usuario(driver, "roncayomesas@gmail.com", "Andres Roncayo", "Diseñador", "Bogota")

    ### CREAR RELACIONES ###
    conecta_con(driver, "ruiz@gmail.com", "roncayomesas@gmail.com")

    print("Datos de prueba cargados correctamente.")

