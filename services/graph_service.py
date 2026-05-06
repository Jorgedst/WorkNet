"""
Service layer para WorkNet — Neo4j integrado.
Mantiene datos mock solo para usuarios/empresas/proyectos de demostración
que ya existen en la BD. Todo lo nuevo se persiste en Neo4j.
"""

import uuid
import random
from datetime import datetime
from models.models import User, Company, Project, JobOffer, Connection, WorksAt
from services.connection import (
    get_driver,
    crear_usuario, crear_empresa, crear_proyecto, crear_oferta, crear_habilidad,
    conecta_con, trabaja_en, tiene_habilidad, participa_en,
    publica_oferta, requiere_habilidad,
)

DB = "005fc815"

# ── Listas predefinidas ────────────────────────────────────────────────────────
PREDEFINED_TITLES = [
    "Software Engineer", "Senior Software Engineer", "Frontend Developer",
    "Backend Developer", "Full Stack Developer", "Data Scientist",
    "Data Engineer", "DevOps Engineer", "Cloud Architect", "UI/UX Designer",
    "Project Manager", "Product Manager", "QA Engineer", "Mobile Developer",
    "Machine Learning Engineer", "Database Administrator", "Systems Analyst",
    "Technical Lead", "Scrum Master", "CTO",
]

PREDEFINED_SKILLS = [
    "JavaScript", "React", "Python", "Node.js", "AI", "B2B", "Java",
    "TypeScript", "Docker", "AWS", "SQL", "MongoDB", "GraphQL", "Neo4j",
    "CSS", "HTML", "Git", "Figma", "Machine Learning", "Data Science",
    "DevOps", "Scrum", "Agile", "C++", "Rust", "Go", "Kotlin", "Swift", "Flutter",
]


# ── Helpers internos ───────────────────────────────────────────────────────────

def _run(query: str, **params):
    """Ejecuta una query de lectura y devuelve lista de records."""
    driver = get_driver()
    with driver.session(database=DB) as s:
        return [r.data() for r in s.run(query, **params)]


def _one(query: str, **params):
    """Ejecuta una query y devuelve el primer record o None."""
    driver = get_driver()
    with driver.session(database=DB) as s:
        return s.run(query, **params).single()


def _neo4j_user_to_model(record: dict) -> User:
    """Convierte un dict de Neo4j en un objeto User."""
    u = record
    name = u.get("nombre", "") or ""
    parts = name.split()
    initials = "".join(p[0].upper() for p in parts[:2])
    avatar_colors = ["#2563eb", "#7c3aed", "#059669", "#dc2626",
                     "#d97706", "#0891b2", "#e11d48", "#4f46e5"]
    color = avatar_colors[hash(u.get("email", "")) % len(avatar_colors)]
    return User(
        id=u.get("email", ""),          # usamos email como id
        name=name,
        email=u.get("email", ""),
        password=u.get("password", ""),
        title=u.get("cargo", ""),
        bio=u.get("bio", ""),
        avatar_color=color,
        initials=initials,
        location=u.get("ciudad", ""),
        skills=u.get("skills", []),
        is_online=True,
    )


def _neo4j_empresa_to_model(record: dict) -> Company:
    e = record
    logo_colors = ["#2563eb", "#7c3aed", "#059669", "#d97706", "#0891b2", "#4f46e5"]
    color = logo_colors[hash(e.get("nombre", "")) % len(logo_colors)]
    name = e.get("nombre", "")
    return Company(
        id=e.get("nombre", ""),         # usamos nombre como id
        name=name,
        description=e.get("descripcion", ""),
        industry=e.get("sector", ""),
        logo_color=color,
        initials=name[0].upper() if name else "?",
        location=e.get("ciudad", ""),
        employee_count=e.get("employee_count", 0),
        founded_year=e.get("founded_year", 0),
    )


def _neo4j_proyecto_to_model(record: dict) -> Project:
    p = record
    techs = p.get("tecnologias", "")
    if isinstance(techs, str):
        techs = [t.strip() for t in techs.split(",") if t.strip()]
    return Project(
        id=p.get("nombre", ""),
        name=p.get("nombre", ""),
        company_id=p.get("empresa_nombre", ""),
        company_name=p.get("empresa_nombre", ""),
        description=p.get("descripcion", ""),
        status="Active",
        technologies=techs,
    )


def _neo4j_oferta_to_model(record: dict, empresa_nombre: str = "") -> JobOffer:
    o = record
    skills = o.get("habilidades", [])
    if isinstance(skills, str):
        skills = [s.strip() for s in skills.split(",") if s.strip()]
    titulo = o.get("titulo", "")
    return JobOffer(
        id=titulo,
        title=titulo,
        company_id=empresa_nombre,
        company_name=empresa_nombre,
        description=o.get("descripcion", ""),
        location=o.get("modalidad", ""),
        salary_range=o.get("salario", "A convenir"),
        job_type="Full-time",
        required_skills=skills,
        posted_date="",
        is_active=True,
        experience_level="",
    )


# ══════════════════════════════════════════════════════════════════════════════
class GraphService:
    """Singleton que conecta las vistas con Neo4j."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._init_local_state()

    def _init_local_state(self):
        """Estado local mínimo: solo sesión y aplicaciones."""
        self.current_user_id = None   # email del usuario logueado
        self._current_user_obj = None  # cached User object
        self._admin_company_obj = None  # cached admin Company (or False if not admin)
        self._cache = {
            "all_users": None,
            "all_companies": None,
            "all_jobs": None,
            "all_projects": None,
            "network_graph_data": None
        }

    def _invalidate_cache(self, keys=None):
        """Limpia el caché para forzar la recarga desde Neo4j."""
        if keys is None:
            keys = self._cache.keys()
        for k in keys:
            self._cache[k] = None

    # ── Autenticación ──────────────────────────────────────────────────────────

    def authenticate(self, email: str, password: str):
        rec = _one(
            "MATCH (u:Usuario {email: $email, password: $password}) "
            "RETURN u",
            email=email, password=password,
        )
        if rec:
            u_data = dict(rec["u"])
            # cargar habilidades
            skills_rec = _run(
                "MATCH (u:Usuario {email: $email})-[:TIENE_HABILIDAD]->(h:Habilidad) "
                "RETURN h.nombre AS nombre",
                email=email,
            )
            u_data["skills"] = [r["nombre"] for r in skills_rec]
            user = _neo4j_user_to_model(u_data)
            self.current_user_id = user.id
            self._current_user_obj = user  # cache for session
            self._admin_company_obj = None  # reset admin cache on login
            return user
        return None

    def get_current_user(self) -> User:
        if not self.current_user_id:
            return None
        if self._current_user_obj and self._current_user_obj.id == self.current_user_id:
            return self._current_user_obj
        user = self.get_user(self.current_user_id)
        self._current_user_obj = user
        return user

    def get_admin_company(self, user_id: str):
        """Devuelve la empresa si el usuario es Administrador."""
        # Return cached result if available
        if self._admin_company_obj is not None:
            return self._admin_company_obj if self._admin_company_obj else None
        
        # Check both the specific ADMINISTRA relationship and the generic TRABAJA_EN
        rec = _one(
            "MATCH (u:Usuario {email: $email})-[r:ADMINISTRA|TRABAJA_EN]->(e:Empresa) "
            "RETURN e LIMIT 1",
            email=user_id,
        )
        if rec:
            company = _neo4j_empresa_to_model(dict(rec["e"]))
            self._admin_company_obj = company
            return company
        self._admin_company_obj = False  # Sentinel: no admin company
        return None

    # ── Usuarios ───────────────────────────────────────────────────────────────

    def get_all_users(self) -> list:
        if self._cache["all_users"] is not None:
            return self._cache["all_users"]
        rows = _run(
            "MATCH (u:Usuario) "
            "OPTIONAL MATCH (u)-[:TIENE_HABILIDAD]->(h:Habilidad) "
            "RETURN u, collect(h.nombre) AS skills"
        )
        users = []
        for r in rows:
            u_data = dict(r["u"])
            u_data["skills"] = r["skills"]
            users.append(_neo4j_user_to_model(u_data))
        self._cache["all_users"] = users
        return users

    def get_user(self, user_id: str) -> User:
        rec = _one(
            "MATCH (u:Usuario {email: $email}) RETURN u",
            email=user_id,
        )
        if not rec:
            return None
        u_data = dict(rec["u"])
        skills_rec = _run(
            "MATCH (u:Usuario {email: $email})-[:TIENE_HABILIDAD]->(h:Habilidad) "
            "RETURN h.nombre AS nombre",
            email=user_id,
        )
        u_data["skills"] = [r["nombre"] for r in skills_rec]
        return _neo4j_user_to_model(u_data)

    def create_user(self, user: User):
        driver = get_driver()
        crear_usuario(driver, user.email, user.name, user.title, user.location or "")
        # Guardar password
        driver.execute_query(
            "MATCH (u:Usuario {email: $email}) SET u.password = $password",
            email=user.email, password=user.password,
            database_=DB,
        )
        # Guardar habilidades
        for skill in user.skills:
            # Asegurarse de que la habilidad exista
            driver.execute_query(
                "MERGE (h:Habilidad {nombre: $nombre}) "
                "ON CREATE SET h.categoria = 'General'",
                nombre=skill, database_=DB,
            )
            tiene_habilidad(driver, user.email, skill)
        self._invalidate_cache(["all_users", "network_graph_data"])
        return user

    def update_user(self, user: User):
        driver = get_driver()
        driver.execute_query(
            "MATCH (u:Usuario {email: $email}) "
            "SET u.nombre = $nombre, u.ciudad = $ciudad",
            email=user.email, nombre=user.name, ciudad=user.location or "",
            database_=DB,
        )
        # Actualizar habilidades: borrar las viejas y poner las nuevas
        driver.execute_query(
            "MATCH (u:Usuario {email: $email})-[r:TIENE_HABILIDAD]->() DELETE r",
            email=user.email, database_=DB,
        )
        for skill in user.skills:
            driver.execute_query(
                "MERGE (h:Habilidad {nombre: $nombre}) "
                "ON CREATE SET h.categoria = 'General'",
                nombre=skill, database_=DB,
            )
            tiene_habilidad(driver, user.email, skill)
        self._invalidate_cache(["all_users"])
        return user

    # ── Conexiones ─────────────────────────────────────────────────────────────

    def get_connections(self, user_id: str) -> list:
        rows = _run(
            "MATCH (u:Usuario {email: $email})-[:CONECTA_CON]-(otro:Usuario) "
            "OPTIONAL MATCH (otro)-[:TIENE_HABILIDAD]->(h:Habilidad) "
            "RETURN otro, collect(h.nombre) AS skills",
            email=user_id,
        )
        users = []
        for r in rows:
            u_data = dict(r["otro"])
            u_data["skills"] = r["skills"]
            users.append(_neo4j_user_to_model(u_data))
        return users

    def is_connected(self, user_id_1: str, user_id_2: str) -> bool:
        rec = _one(
            "MATCH (a:Usuario {email: $e1})-[:CONECTA_CON]-(b:Usuario {email: $e2}) "
            "RETURN count(*) AS n",
            e1=user_id_1, e2=user_id_2,
        )
        return rec and rec["n"] > 0

    def send_connection_request(self, user_id_1: str, user_id_2: str):
        if self.is_connected(user_id_1, user_id_2):
            return False
        driver = get_driver()
        conecta_con(driver, user_id_1, user_id_2)
        self._invalidate_cache(["network_graph_data"])
        return True

    def get_common_connections(self, user_id_1: str, user_id_2: str) -> list:
        rows = _run(
            "MATCH (a:Usuario {email: $e1})-[:CONECTA_CON]->(comun:Usuario)"
            "<-[:CONECTA_CON]-(b:Usuario {email: $e2}) "
            "RETURN comun",
            e1=user_id_1, e2=user_id_2,
        )
        return [_neo4j_user_to_model(dict(r["comun"])) for r in rows]

    # ── Empresas ───────────────────────────────────────────────────────────────

    def get_all_companies(self) -> list:
        if self._cache["all_companies"] is not None:
            return self._cache["all_companies"]
        rows = _run(
            "MATCH (e:Empresa) "
            "OPTIONAL MATCH (u:Usuario)-[:TRABAJA_EN]->(e) "
            "RETURN e, count(u) AS total"
        )
        companies = []
        for r in rows:
            e_data = dict(r["e"])
            c = _neo4j_empresa_to_model(e_data)
            c.employee_count = r["total"]
            companies.append(c)
        self._cache["all_companies"] = companies
        return companies

    def get_company(self, company_id: str) -> Company:
        rec = _one(
            "MATCH (e:Empresa {nombre: $nombre}) RETURN e",
            nombre=company_id,
        )
        if rec:
            return _neo4j_empresa_to_model(dict(rec["e"]))
        return None

    def create_company(self, company: Company):
        driver = get_driver()
        crear_empresa(driver, company.name, company.location, company.industry)
        self._invalidate_cache(["all_companies", "network_graph_data"])
        return company

    def get_company_employees(self, company_id: str) -> list:
        rows = _run(
            "MATCH (u:Usuario)-[:TRABAJA_EN]->(e:Empresa {nombre: $nombre}) "
            "OPTIONAL MATCH (u)-[:TIENE_HABILIDAD]->(h:Habilidad) "
            "RETURN u, collect(h.nombre) AS skills",
            nombre=company_id,
        )
        users = []
        for r in rows:
            u_data = dict(r["u"])
            u_data["skills"] = r["skills"]
            users.append(_neo4j_user_to_model(u_data))
        return users

    def get_user_company(self, user_id: str) -> Company:
        rec = _one(
            "MATCH (u:Usuario {email: $email})-[:TRABAJA_EN]->(e:Empresa) "
            "RETURN e",
            email=user_id,
        )
        if rec:
            return _neo4j_empresa_to_model(dict(rec["e"]))
        return None

    # ── Proyectos ──────────────────────────────────────────────────────────────

    def get_all_projects(self) -> list:
        if self._cache["all_projects"] is not None:
            return self._cache["all_projects"]
        rows = _run(
            "MATCH (p:Proyecto) "
            "OPTIONAL MATCH (e:Empresa)-[:PUBLICA]->(o:Oferta)<-[:PERTENECE_A]-(p) "
            "OPTIONAL MATCH (e2:Empresa)-[:PUBLICA_PROYECTO]->(p) "
            "RETURN p, coalesce(e2.nombre, e.nombre, '') AS empresa_nombre"
        )
        projs = [_neo4j_proyecto_to_model({**dict(r["p"]), "empresa_nombre": r["empresa_nombre"]})
                for r in rows]
        self._cache["all_projects"] = projs
        return projs

    def get_project(self, project_id: str) -> Project:
        rec = _one(
            "MATCH (p:Proyecto {nombre: $nombre}) RETURN p",
            nombre=project_id,
        )
        if rec:
            return _neo4j_proyecto_to_model(dict(rec["p"]))
        return None

    def get_company_projects(self, company_id: str) -> list:
        """Proyectos que pertenecen a esta empresa (vía PUBLICA_PROYECTO o vía ofertas)."""
        # 1. Try direct PUBLICA_PROYECTO relationship first
        rows = _run(
            "MATCH (e:Empresa {nombre: $nombre})-[:PUBLICA_PROYECTO]->(p:Proyecto) "
            "RETURN DISTINCT p, e.nombre AS empresa_nombre",
            nombre=company_id,
        )
        # 2. Also include projects linked via offers published by this company
        if not rows:
            rows = _run(
                "MATCH (e:Empresa {nombre: $nombre})-[:PUBLICA]->(o:Oferta)<-[:PERTENECE_A]-(p:Proyecto) "
                "RETURN DISTINCT p, e.nombre AS empresa_nombre",
                nombre=company_id,
            )
        # No fallback — only return this company's projects
        return [_neo4j_proyecto_to_model({**dict(r["p"]), "empresa_nombre": r.get("empresa_nombre", "")})
                for r in rows]

    def get_user_projects(self, user_id: str) -> list:
        rows = _run(
            "MATCH (u:Usuario {email: $email})-[:PARTICIPA_EN]->(p:Proyecto) "
            "RETURN p",
            email=user_id,
        )
        return [_neo4j_proyecto_to_model(dict(r["p"])) for r in rows]

    def get_project_members(self, project_id: str) -> list:
        rows = _run(
            "MATCH (u:Usuario)-[:PARTICIPA_EN]->(p:Proyecto {nombre: $nombre}) "
            "OPTIONAL MATCH (u)-[:TIENE_HABILIDAD]->(h:Habilidad) "
            "RETURN u, collect(h.nombre) AS skills",
            nombre=project_id,
        )
        users = []
        for r in rows:
            u_data = dict(r["u"])
            u_data["skills"] = r["skills"]
            users.append(_neo4j_user_to_model(u_data))
        return users

    def create_project(self, project: Project):
        driver = get_driver()
        techs = ", ".join(project.technologies) if project.technologies else ""
        crear_proyecto(driver, project.description, project.name, techs)
        if project.company_name:
            driver.execute_query(
                "MATCH (e:Empresa {nombre: $empresa}) MATCH (p:Proyecto {nombre: $proyecto}) MERGE (e)-[:PUBLICA_PROYECTO]->(p)",
                empresa=project.company_name, proyecto=project.name, database_=DB
            )
        self._invalidate_cache(["all_projects"])
        return project

    # ── Ofertas ────────────────────────────────────────────────────────────────

    def get_all_jobs(self) -> list:
        if self._cache["all_jobs"] is not None:
            return self._cache["all_jobs"]
        rows = _run(
            "MATCH (e:Empresa)-[:PUBLICA]->(o:Oferta) "
            "OPTIONAL MATCH (p:Proyecto)-[:PERTENECE_A]->(o) "
            "OPTIONAL MATCH (o)-[:REQUIERE]->(h:Habilidad) "
            "RETURN o, e.nombre AS empresa_nombre, p.nombre AS proyecto_nombre, collect(h.nombre) AS habilidades"
        )
        jobs = []
        for r in rows:
            o_data = dict(r["o"])
            o_data["habilidades"] = r["habilidades"]
            job = _neo4j_oferta_to_model(o_data, r["empresa_nombre"])
            if r.get("proyecto_nombre"):
                job.project_id = r["proyecto_nombre"]
                job.project_name = r["proyecto_nombre"]
            jobs.append(job)
        self._cache["all_jobs"] = jobs
        return jobs

    def get_job(self, job_id: str) -> JobOffer:
        rec = _one(
            "MATCH (e:Empresa)-[:PUBLICA]->(o:Oferta {titulo: $titulo}) "
            "OPTIONAL MATCH (p:Proyecto)-[:PERTENECE_A]->(o) "
            "OPTIONAL MATCH (o)-[:REQUIERE]->(h:Habilidad) "
            "RETURN o, e.nombre AS empresa_nombre, p.nombre AS proyecto_nombre, collect(h.nombre) AS habilidades",
            titulo=job_id,
        )
        if rec:
            o_data = dict(rec["o"])
            o_data["habilidades"] = rec["habilidades"]
            job = _neo4j_oferta_to_model(o_data, rec["empresa_nombre"])
            if rec.get("proyecto_nombre"):
                job.project_id = rec["proyecto_nombre"]
                job.project_name = rec["proyecto_nombre"]
            return job
        return None

    def get_project_jobs(self, project_id: str) -> list:
        rows = _run(
            "MATCH (p:Proyecto {nombre: $proyecto})-[:PERTENECE_A]->(o:Oferta) "
            "MATCH (e:Empresa)-[:PUBLICA]->(o) "
            "OPTIONAL MATCH (o)-[:REQUIERE]->(h:Habilidad) "
            "RETURN o, e.nombre AS empresa_nombre, collect(h.nombre) AS habilidades",
            proyecto=project_id
        )
        jobs = []
        for r in rows:
            o_data = dict(r["o"])
            o_data["habilidades"] = r["habilidades"]
            job = _neo4j_oferta_to_model(o_data, r["empresa_nombre"])
            job.project_id = project_id
            job.project_name = project_id
            jobs.append(job)
        return jobs

    def get_company_jobs(self, company_id: str) -> list:
        rows = _run(
            "MATCH (e:Empresa {nombre: $nombre})-[:PUBLICA]->(o:Oferta) "
            "OPTIONAL MATCH (o)-[:REQUIERE]->(h:Habilidad) "
            "RETURN o, e.nombre AS empresa_nombre, collect(h.nombre) AS habilidades",
            nombre=company_id,
        )
        jobs = []
        for r in rows:
            o_data = dict(r["o"])
            o_data["habilidades"] = r["habilidades"]
            jobs.append(_neo4j_oferta_to_model(o_data, r["empresa_nombre"]))
        return jobs

    def create_job(self, job: JobOffer):
        driver = get_driver()
        crear_oferta(driver, job.title, job.salary_range or "A convenir", job.location or "")
        if job.company_name:
            publica_oferta(driver, job.company_name, job.title)
        if job.project_name:
            driver.execute_query(
                "MATCH (p:Proyecto {nombre: $proyecto}) MATCH (o:Oferta {titulo: $oferta}) MERGE (p)-[:PERTENECE_A]->(o)",
                proyecto=job.project_name, oferta=job.title, database_=DB
            )
        for skill in job.required_skills:
            driver.execute_query(
                "MERGE (h:Habilidad {nombre: $nombre}) ON CREATE SET h.categoria = 'General'",
                nombre=skill, database_=DB,
            )
            requiere_habilidad(driver, job.title, skill)
        self._invalidate_cache(["all_jobs"])
        return job

    def apply_to_job(self, user_id: str, job_id: str):
        driver = get_driver()
        driver.execute_query(
            "MATCH (u:Usuario {email: $email}) MATCH (o:Oferta {titulo: $titulo}) MERGE (u)-[:APLICA_A]->(o)",
            email=user_id, titulo=job_id, database_=DB
        )
        return True

    def has_applied(self, user_id: str, job_id: str) -> bool:
        rec = _one(
            "MATCH (u:Usuario {email: $email})-[:APLICA_A]->(o:Oferta {titulo: $titulo}) RETURN count(o) as n",
            email=user_id, titulo=job_id
        )
        return rec and rec["n"] > 0

    def get_user_applications(self, user_id: str) -> list:
        rows = _run(
            "MATCH (u:Usuario {email: $email})-[:APLICA_A]->(o:Oferta) RETURN o.titulo as job_id",
            email=user_id
        )
        return [r["job_id"] for r in rows]

    def get_job_applicants_count(self, job_id: str) -> int:
        """Return how many users have applied to a specific job vacancy."""
        rec = _one(
            "MATCH (u:Usuario)-[:APLICA_A]->(o:Oferta {titulo: $titulo}) RETURN count(u) as n",
            titulo=job_id
        )
        return rec["n"] if rec else 0

    # ── Análisis de grafos ─────────────────────────────────────────────────────

    def get_users_with_similar_skills(self, user_id: str) -> list:
        rows = _run(
            "MATCH (u:Usuario {email: $email})-[:TIENE_HABILIDAD]->(h:Habilidad)"
            "<-[:TIENE_HABILIDAD]-(otro:Usuario) "
            "WHERE otro.email <> $email "
            "WITH otro, collect(h.nombre) AS shared, count(h) AS total "
            "ORDER BY total DESC "
            "RETURN otro, shared, total",
            email=user_id,
        )
        result = []
        for r in rows:
            u_data = dict(r["otro"])
            u_data["skills"] = r["shared"]
            other = _neo4j_user_to_model(u_data)
            result.append((other, r["total"], r["shared"]))
        return result

    def get_recommendations(self, user_id: str) -> list:
        connected = {u.id for u in self.get_connections(user_id)} | {user_id}
        rows = _run(
            "MATCH (u:Usuario {email: $email})-[:TIENE_HABILIDAD]->(h:Habilidad)"
            "<-[:TIENE_HABILIDAD]-(rec:Usuario) "
            "WHERE rec.email <> $email "
            "WITH rec, collect(DISTINCT h.nombre) AS shared, count(DISTINCT h) AS score "
            "ORDER BY score DESC "
            "RETURN rec, shared, score",
            email=user_id,
        )
        result = []
        for r in rows:
            u_data = dict(r["rec"])
            u_data["skills"] = r["shared"]
            other = _neo4j_user_to_model(u_data)
            if other.id not in connected:
                result.append((other, r["score"], r["shared"], []))
        return result

    def get_shortest_path(self, start_id: str, end_id: str) -> list:
        rec = _one(
            "MATCH (a:Usuario {email: $start}), (b:Usuario {email: $end}), "
            "path = shortestPath((a)-[*..6]-(b)) "
            "RETURN [n IN nodes(path) | coalesce(n.nombre, n.titulo)] AS ruta",
            start=start_id, end=end_id,
        )
        if rec:
            return rec["ruta"]
        return []

    def get_network_graph_data(self) -> dict:
        if self._cache["network_graph_data"] is not None:
            return self._cache["network_graph_data"]

        rows = _run("""
            MATCH (a)-[r:CONECTA_CON|TRABAJA_EN|PUBLICA]->(b)
            WHERE (a:Usuario OR a:Empresa) AND (b:Usuario OR b:Empresa OR b:Oferta)
            RETURN
                coalesce(a.email, a.nombre) AS from_id,
                coalesce(a.nombre, a.email) AS from_label,
                labels(a)[0] AS from_type,
                coalesce(b.email, b.nombre, b.titulo) AS to_id,
                coalesce(b.nombre, b.titulo, b.email) AS to_label,
                labels(b)[0] AS to_type,
                type(r) AS rel_type
        """)

        avatar_colors = ["#2563eb", "#7c3aed", "#059669", "#dc2626",
                        "#d97706", "#0891b2", "#e11d48", "#4f46e5"]
        logo_colors   = ["#4f46e5", "#7c3aed", "#059669", "#d97706", "#0891b2"]

        type_map = {"Usuario": "user", "Empresa": "company", "Oferta": "job"}
        nodes_seen = {}
        edges = []

        for r in rows:
            for nid, nlabel, ntype in [
                (r["from_id"], r["from_label"], r["from_type"]),
                (r["to_id"],   r["to_label"],   r["to_type"]),
            ]:
                if nid and nid not in nodes_seen:
                    t = type_map.get(ntype, "user")
                    if t == "user":
                        color = avatar_colors[hash(nid) % len(avatar_colors)]
                    elif t == "company":
                        color = logo_colors[hash(nid) % len(logo_colors)]
                    else:
                        color = "#e11d48"
                    nodes_seen[nid] = {"id": nid, "label": nlabel, "type": t, "color": color}

            if r["from_id"] and r["to_id"]:
                edges.append({"from": r["from_id"], "to": r["to_id"], "type": r["rel_type"]})

        data = {"nodes": list(nodes_seen.values()), "edges": edges}
        self._cache["network_graph_data"] = data
        return data

    def get_skill_match_percent(self, user_id: str, job_id: str) -> int:
        user = self.get_user(user_id)
        job = self.get_job(job_id)
        if not user or not job or not job.required_skills:
            return 0
        user_skills = set(user.skills)
        job_skills = set(job.required_skills)
        if not job_skills:
            return 0
        return int(len(user_skills & job_skills) / len(job_skills) * 100)

    # ── Compatibilidad con works_at local (company register) ──────────────────

    @property
    def works_at(self):
        """Propiedad de compatibilidad — devuelve lista vacía."""
        if not hasattr(self, "_works_at"):
            self._works_at = []
        return self._works_at

    def close(self):
        driver = get_driver()
        if driver:
            driver.close()
