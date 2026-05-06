
# Rol 3 — Especialista en Lógica de Grafos
# Todas las consultas Cypher del proyecto WorkNet

# ──────────────────────────────────────────────
# IMPORTACIÓN  (el driver lo crea el Rol 2)
# ──────────────────────────────────────────────
# from services.connection import get_driver
# driver = get_driver()


DB = "005fc815"


def usuarios_con_habilidades_similares(driver, email_usuario: str) -> list:
    query = """
    MATCH (u:Usuario {email: $email})-[:TIENE_HABILIDAD]->(h:Habilidad)
          <-[:TIENE_HABILIDAD]-(otro:Usuario)
    WHERE otro.email <> $email
    RETURN otro.nombre           AS usuario,
           collect(h.nombre)     AS habilidades_comunes,
           count(h)              AS total_comunes
    ORDER BY total_comunes DESC
    """
    with driver.session(database=DB) as session:
        return [r.data() for r in session.run(query, email=email_usuario)]


def contactos_en_comun(driver, email_a: str, email_b: str) -> list:
    query = """
    MATCH (a:Usuario {email: $email_a})-[:CONECTA_CON]->(comun:Usuario)
          <-[:CONECTA_CON]-(b:Usuario {email: $email_b})
    RETURN comun.nombre AS contacto_comun,
           comun.cargo  AS cargo
    """
    with driver.session(database=DB) as session:
        return [r.data() for r in session.run(query, email_a=email_a, email_b=email_b)]


def ruta_mas_corta(driver, email_usuario: str, nombre_empresa: str) -> dict:
    query = """
    MATCH (u:Usuario {email: $email}),
          (e:Empresa  {nombre: $empresa}),
          path = shortestPath((u)-[*..6]-(e))
    RETURN [n IN nodes(path) | 
            CASE
              WHEN n:Usuario  THEN n.nombre
              WHEN n:Empresa  THEN n.nombre
              WHEN n:Habilidad THEN n.nombre
              WHEN n:Proyecto  THEN n.nombre
              WHEN n:Oferta    THEN n.titulo
            END] AS ruta,
           length(path) AS pasos
    """
    with driver.session(database=DB) as session:
        record = session.run(
            query, email=email_usuario, empresa=nombre_empresa).single()
        if record:
            return {"ruta": record["ruta"], "pasos": record["pasos"]}
        return {"ruta": [], "pasos": -1, "mensaje": "Sin conexión encontrada"}


def candidatos_para_oferta(driver, titulo_oferta: str) -> list:
    query = """
    MATCH (o:Oferta {titulo: $oferta})-[:REQUIERE]->(h:Habilidad)
          <-[:TIENE_HABILIDAD]-(u:Usuario)
    WITH u, o, count(h) AS habilidades_match
    OPTIONAL MATCH (u)-[:CONECTA_CON]->(:Usuario)-[:TRABAJA_EN]->
                   (:Empresa)-[:PUBLICA]->(o)
    WITH u, habilidades_match, count(*) AS conexiones_internas
    RETURN u.nombre           AS candidato,
           u.email            AS email,
           habilidades_match,
           conexiones_internas,
           (habilidades_match * 3 + conexiones_internas) AS puntaje
    ORDER BY puntaje DESC
    LIMIT 10
    """
    with driver.session(database=DB) as session:
        return [r.data() for r in session.run(query, oferta=titulo_oferta)]


def proyectos_relacionados(driver, nombre_proyecto: str) -> list:
    query = """
    MATCH (p:Proyecto {nombre: $proyecto})
    OPTIONAL MATCH (p)<-[:PARTICIPA_EN]-(u:Usuario)-[:PARTICIPA_EN]->(otro:Proyecto)
    WHERE otro.nombre <> p.nombre
    WITH p, collect(DISTINCT {proyecto: otro.nombre,
                               vinculo: 'miembro compartido'}) AS por_miembro
    OPTIONAL MATCH (p)<-[:PARTICIPA_EN]-(:Usuario)-[:TIENE_HABILIDAD]->(h:Habilidad)
                   <-[:TIENE_HABILIDAD]-(:Usuario)-[:PARTICIPA_EN]->(otro2:Proyecto)
    WHERE otro2.nombre <> p.nombre
    WITH por_miembro,
         collect(DISTINCT {proyecto: otro2.nombre,
                            vinculo: 'habilidad compartida'}) AS por_habilidad
    WITH por_miembro + por_habilidad AS todos
    RETURN [x IN todos WHERE x.proyecto IS NOT NULL] AS proyectos_relacionados
    """
    with driver.session(database=DB) as session:
        record = session.run(query, proyecto=nombre_proyecto).single()
        return record["proyectos_relacionados"] if record else []