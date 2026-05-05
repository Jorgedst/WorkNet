"""
Service layer for graph database operations.
Currently uses mock data. Replace methods with Neo4j Cypher queries.

Neo4j Integration Guide:
    1. pip install neo4j
    2. from neo4j import GraphDatabase
    3. self.driver = GraphDatabase.driver(uri, auth=(user, password))
    4. Replace each method body with session.run(cypher_query, params)
"""

from models.models import User, Company, Project, JobOffer, Connection, WorksAt

# ── Predefined Lists ──────────────────────────────────────
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


class GraphService:
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
        self._init_mock_data()

    def _init_mock_data(self):
        self.current_user_id = "u1"

        self.users = {
            "u1": User(id="u1", name="Sarah López", email="sarah@worknet.com", password="admin123",
                       title="Senior Software Engineer", bio="Passionate about building scalable systems.",
                       avatar_color="#2563eb", location="Bogotá, Colombia",
                       skills=["Python", "React", "Docker", "AWS"], is_online=True),
            "u2": User(id="u2", name="Michael Chen", email="michael@worknet.com", password="1234",
                       title="Senior Software Engineer", avatar_color="#7c3aed",
                       location="San Francisco, USA",
                       skills=["JavaScript", "React", "Python", "AI", "Node.js"], is_online=True),
            "u3": User(id="u3", name="Robert Smith", email="robert@worknet.com", password="1234",
                       title="Full Stack Developer", avatar_color="#059669",
                       location="New York, USA",
                       skills=["JavaScript", "React", "Python", "Node.js"], is_online=False),
            "u4": User(id="u4", name="Robert Chen", email="rchen@worknet.com", password="1234",
                       title="Backend Developer", avatar_color="#dc2626",
                       location="Austin, USA",
                       skills=["JavaScript", "React", "Python", "B2B", "AI", "Node.js"], is_online=True),
            "u5": User(id="u5", name="Julia Lee", email="julia@worknet.com", password="1234",
                       title="Frontend Developer", avatar_color="#d97706",
                       location="London, UK",
                       skills=["JavaScript", "React", "TypeScript", "CSS", "Figma"], is_online=False),
            "u6": User(id="u6", name="Alice Wong", email="alice@worknet.com", password="1234",
                       title="Data Scientist", avatar_color="#0891b2",
                       location="Toronto, Canada",
                       skills=["Python", "Machine Learning", "Data Science", "SQL"], is_online=True),
            "u7": User(id="u7", name="Carlos Méndez", email="carlos@worknet.com", password="1234",
                       title="DevOps Engineer", avatar_color="#4f46e5",
                       location="Madrid, Spain",
                       skills=["Docker", "AWS", "DevOps", "Python", "Go"], is_online=False),
            "u8": User(id="u8", name="Diana Torres", email="diana@worknet.com", password="1234",
                       title="Frontend Developer", avatar_color="#e11d48",
                       location="Medellín, Colombia",
                       skills=["React", "TypeScript", "CSS", "Figma", "Node.js"], is_online=True),
        }

        self.companies = {
            "c1": Company(id="c1", name="TechCorp", description="Leading technology solutions provider.",
                          industry="Technology", logo_color="#2563eb", location="San Francisco, USA",
                          employee_count=5000, founded_year=2010),
            "c2": Company(id="c2", name="InnovateSolutions", description="AI-driven innovation company.",
                          industry="AI & Machine Learning", logo_color="#7c3aed", location="New York, USA",
                          employee_count=1200, founded_year=2015),
            "c3": Company(id="c3", name="Vertex Inc.", description="Cloud infrastructure and services.",
                          industry="Cloud Computing", logo_color="#059669", location="Austin, USA",
                          employee_count=3000, founded_year=2012),
            "c4": Company(id="c4", name="DataFlow", description="Big data analytics platform.",
                          industry="Data Analytics", logo_color="#d97706", location="London, UK",
                          employee_count=800, founded_year=2018),
        }

        # Projects published by companies
        self.projects = {
            "p1": Project(id="p1", name="AI Recommendation Engine",
                          company_id="c1", company_name="TechCorp",
                          description="ML-powered recommendation system for e-commerce.",
                          status="Active", technologies=["Python", "Machine Learning", "Docker"]),
            "p2": Project(id="p2", name="Cloud Migration Platform",
                          company_id="c3", company_name="Vertex Inc.",
                          description="Enterprise cloud migration automation tools.",
                          status="Active", technologies=["AWS", "Docker", "DevOps", "Go"]),
            "p3": Project(id="p3", name="Mobile App Redesign",
                          company_id="c1", company_name="TechCorp",
                          description="Complete UI/UX overhaul of flagship mobile app.",
                          status="Active", technologies=["React", "TypeScript", "Figma"]),
            "p4": Project(id="p4", name="Graph Analytics Platform",
                          company_id="c2", company_name="InnovateSolutions",
                          description="Network analysis and visualization using Neo4j.",
                          status="Active", technologies=["Neo4j", "Python", "GraphQL", "React"]),
            "p5": Project(id="p5", name="Data Pipeline Modernization",
                          company_id="c4", company_name="DataFlow",
                          description="Rebuilding ETL pipelines with modern streaming tech.",
                          status="Active", technologies=["Python", "SQL", "AWS", "Docker"]),
        }

        # Vacantes linked to projects and companies
        self.jobs = {
            "j1": JobOffer(id="j1", title="Senior Python Developer",
                           company_id="c1", company_name="TechCorp",
                           project_id="p1", project_name="AI Recommendation Engine",
                           description="Build ML recommendation models.",
                           location="San Francisco (Remote)", salary_range="$120k-$160k",
                           job_type="Full-time", required_skills=["Python", "Machine Learning", "Docker"],
                           posted_date="2026-04-28", experience_level="Senior"),
            "j2": JobOffer(id="j2", title="ML Engineer",
                           company_id="c1", company_name="TechCorp",
                           project_id="p1", project_name="AI Recommendation Engine",
                           description="Develop and deploy ML pipelines.",
                           location="San Francisco (Hybrid)", salary_range="$130k-$170k",
                           job_type="Full-time", required_skills=["Python", "AI", "Machine Learning"],
                           posted_date="2026-05-01", experience_level="Mid"),
            "j3": JobOffer(id="j3", title="React Frontend Engineer",
                           company_id="c2", company_name="InnovateSolutions",
                           project_id="p4", project_name="Graph Analytics Platform",
                           description="Build interactive graph visualization UIs.",
                           location="New York (Hybrid)", salary_range="$100k-$140k",
                           job_type="Full-time", required_skills=["React", "TypeScript", "GraphQL"],
                           posted_date="2026-05-01", experience_level="Mid"),
            "j4": JobOffer(id="j4", title="DevOps Engineer",
                           company_id="c3", company_name="Vertex Inc.",
                           project_id="p2", project_name="Cloud Migration Platform",
                           description="Manage CI/CD and cloud infrastructure.",
                           location="Austin, USA", salary_range="$115k-$155k",
                           job_type="Full-time", required_skills=["Docker", "AWS", "DevOps", "Go"],
                           posted_date="2026-05-02", experience_level="Mid"),
            "j5": JobOffer(id="j5", title="Cloud Architect",
                           company_id="c3", company_name="Vertex Inc.",
                           project_id="p2", project_name="Cloud Migration Platform",
                           description="Design scalable cloud architectures.",
                           location="Austin (Remote)", salary_range="$140k-$180k",
                           job_type="Full-time", required_skills=["AWS", "Docker", "DevOps"],
                           posted_date="2026-04-30", experience_level="Senior"),
            "j6": JobOffer(id="j6", title="UI/UX Designer",
                           company_id="c1", company_name="TechCorp",
                           project_id="p3", project_name="Mobile App Redesign",
                           description="Lead the redesign of mobile interfaces.",
                           location="San Francisco (Remote)", salary_range="$90k-$130k",
                           job_type="Full-time", required_skills=["Figma", "CSS", "React"],
                           posted_date="2026-05-03", experience_level="Mid"),
            "j7": JobOffer(id="j7", title="Data Engineer",
                           company_id="c4", company_name="DataFlow",
                           project_id="p5", project_name="Data Pipeline Modernization",
                           description="Build modern data pipelines.",
                           location="London (Remote)", salary_range="$100k-$140k",
                           job_type="Full-time", required_skills=["Python", "SQL", "AWS", "Docker"],
                           posted_date="2026-04-25", experience_level="Senior"),
        }

        # Relación: CONECTA_CON
        self.connections = [
            Connection("u1", "u2", "professional", "2025-06-15", "accepted"),
            Connection("u1", "u3", "colleague", "2025-08-20", "accepted"),
            Connection("u1", "u6", "professional", "2025-11-01", "accepted"),
            Connection("u1", "u8", "colleague", "2026-01-10", "accepted"),
            Connection("u2", "u3", "professional", "2025-05-10", "accepted"),
            Connection("u2", "u4", "colleague", "2025-09-12", "accepted"),
            Connection("u3", "u5", "professional", "2025-07-22", "accepted"),
            Connection("u4", "u5", "colleague", "2025-10-05", "accepted"),
            Connection("u5", "u6", "professional", "2026-01-15", "accepted"),
            Connection("u6", "u7", "colleague", "2025-12-01", "accepted"),
            Connection("u7", "u8", "professional", "2026-02-14", "accepted"),
        ]

        # Relación: TRABAJA_EN
        self.works_at = [
            WorksAt("u1", "c1", "Senior Engineer", "2023-01-15", is_current=True),
            WorksAt("u2", "c1", "Software Engineer", "2022-06-01", is_current=True),
            WorksAt("u3", "c2", "Lead Developer", "2024-03-01", is_current=True),
            WorksAt("u4", "c2", "Software Engineer", "2023-08-15", is_current=True),
            WorksAt("u5", "c3", "Senior Developer", "2022-11-01", is_current=True),
            WorksAt("u6", "c4", "Data Scientist", "2024-01-10", is_current=True),
            WorksAt("u7", "c3", "DevOps Engineer", "2023-05-20", is_current=True),
            WorksAt("u8", "c1", "Frontend Developer", "2024-06-01", is_current=True),
        ]

        # Relación: PARTICIPA_EN (users participating in projects)
        self.participations = [
            {"user_id": "u1", "project_id": "p1", "role": "Lead"},
            {"user_id": "u2", "project_id": "p1", "role": "Member"},
            {"user_id": "u6", "project_id": "p1", "role": "Member"},
            {"user_id": "u7", "project_id": "p2", "role": "Lead"},
            {"user_id": "u5", "project_id": "p2", "role": "Member"},
            {"user_id": "u8", "project_id": "p3", "role": "Lead"},
            {"user_id": "u3", "project_id": "p3", "role": "Member"},
            {"user_id": "u6", "project_id": "p4", "role": "Lead"},
            {"user_id": "u1", "project_id": "p4", "role": "Member"},
            {"user_id": "u6", "project_id": "p5", "role": "Member"},
        ]

        # Applications tracking
        self.applications = []  # {"user_id": ..., "job_id": ...}

    # ── Authentication ─────────────────────────────────────
    def authenticate(self, email: str, password: str):
        """TODO Neo4j: MATCH (u:User {email: $email, password: $password}) RETURN u"""
        for user in self.users.values():
            if user.email == email and user.password == password:
                self.current_user_id = user.id
                return user
        return None

    def get_current_user(self):
        return self.users.get(self.current_user_id)

    def get_admin_company(self, user_id: str):
        """Check if user is a company admin and return the company if so."""
        for w in self.works_at:
            if w.user_id == user_id and w.role == "Administrador" and w.is_current:
                return self.get_company(w.company_id)
        return None

    # ── User CRUD ──────────────────────────────────────────
    def get_all_users(self):
        return list(self.users.values())

    def get_user(self, user_id: str):
        return self.users.get(user_id)

    def create_user(self, user: User):
        self.users[user.id] = user
        return user

    def update_user(self, user: User):
        self.users[user.id] = user
        return user

    # ── Connection Operations ──────────────────────────────
    def get_connections(self, user_id: str):
        """TODO Neo4j: MATCH (u:User {id:$id})-[:CONECTA_CON]-(other:User) RETURN other"""
        connected_ids = []
        for c in self.connections:
            if c.status != "accepted":
                continue
            if c.user_id_1 == user_id:
                connected_ids.append(c.user_id_2)
            elif c.user_id_2 == user_id:
                connected_ids.append(c.user_id_1)
        return [self.users[uid] for uid in connected_ids if uid in self.users]

    def is_connected(self, user_id_1: str, user_id_2: str):
        for c in self.connections:
            if c.status == "accepted":
                if (c.user_id_1 == user_id_1 and c.user_id_2 == user_id_2) or \
                   (c.user_id_1 == user_id_2 and c.user_id_2 == user_id_1):
                    return True
        return False

    def send_connection_request(self, user_id_1: str, user_id_2: str):
        """TODO Neo4j: CREATE (u1)-[:CONECTA_CON {status: 'pending'}]->(u2)"""
        # Check if already connected or pending
        for c in self.connections:
            if (c.user_id_1 == user_id_1 and c.user_id_2 == user_id_2) or \
               (c.user_id_1 == user_id_2 and c.user_id_2 == user_id_1):
                return False
        from datetime import datetime
        self.connections.append(
            Connection(user_id_1, user_id_2, "professional", datetime.now().strftime("%Y-%m-%d"), "pending")
        )
        return True

    def get_common_connections(self, user_id_1: str, user_id_2: str):
        """TODO Neo4j: MATCH (u1)-[:CONECTA_CON]-(common)-[:CONECTA_CON]-(u2) RETURN common"""
        conns1 = {u.id for u in self.get_connections(user_id_1)}
        conns2 = {u.id for u in self.get_connections(user_id_2)}
        common_ids = conns1 & conns2
        return [self.users[uid] for uid in common_ids if uid in self.users]

    # ── Company Operations ─────────────────────────────────
    def get_all_companies(self):
        return list(self.companies.values())

    def get_company(self, company_id: str):
        return self.companies.get(company_id)

    def create_company(self, company: Company):
        """TODO Neo4j: CREATE (c:Company {props}) RETURN c"""
        self.companies[company.id] = company
        return company

    def get_company_employees(self, company_id: str):
        """TODO Neo4j: MATCH (u:User)-[:TRABAJA_EN]->(c:Company {id:$id}) RETURN u"""
        emp_ids = [w.user_id for w in self.works_at if w.company_id == company_id and w.is_current]
        return [self.users[uid] for uid in emp_ids if uid in self.users]

    def get_user_company(self, user_id: str):
        for w in self.works_at:
            if w.user_id == user_id and w.is_current:
                return self.companies.get(w.company_id)
        return None

    def get_company_projects(self, company_id: str):
        """TODO Neo4j: MATCH (c:Company {id:$id})-[:PUBLICA]->(p:Project) RETURN p"""
        return [p for p in self.projects.values() if p.company_id == company_id]

    def get_company_jobs(self, company_id: str):
        return [j for j in self.jobs.values() if j.company_id == company_id and j.is_active]

    # ── Job/Vacancy Operations ─────────────────────────────
    def get_all_jobs(self):
        return list(self.jobs.values())

    def get_job(self, job_id: str):
        return self.jobs.get(job_id)

    def get_project_jobs(self, project_id: str):
        """TODO Neo4j: MATCH (p:Project {id:$id})<-[:PERTENECE_A]-(j:Oferta) RETURN j"""
        return [j for j in self.jobs.values() if j.project_id == project_id and j.is_active]

    def apply_to_job(self, user_id: str, job_id: str):
        """TODO Neo4j: CREATE (u:User {id:$uid})-[:APLICA_A]->(j:Oferta {id:$jid})"""
        self.applications.append({"user_id": user_id, "job_id": job_id})
        return True

    def has_applied(self, user_id: str, job_id: str):
        return any(a["user_id"] == user_id and a["job_id"] == job_id for a in self.applications)

    def create_job(self, job: JobOffer):
        self.jobs[job.id] = job
        return job

    # ── Project Operations ─────────────────────────────────
    def get_all_projects(self):
        return list(self.projects.values())

    def get_project(self, project_id: str):
        return self.projects.get(project_id)

    def get_project_members(self, project_id: str):
        member_ids = [p["user_id"] for p in self.participations if p["project_id"] == project_id]
        return [self.users[uid] for uid in member_ids if uid in self.users]

    def get_user_projects(self, user_id: str):
        proj_ids = [p["project_id"] for p in self.participations if p["user_id"] == user_id]
        return [self.projects[pid] for pid in proj_ids if pid in self.projects]

    def create_project(self, project: Project):
        self.projects[project.id] = project
        return project

    # ── Graph Analysis Queries ─────────────────────────────
    def get_users_with_similar_skills(self, user_id: str):
        """
        TODO Neo4j: MATCH (u1:User {id:$id})-[:TIENE_HABILIDAD]->(s:Skill)<-[:TIENE_HABILIDAD]-(u2:User)
                    WHERE u1 <> u2 RETURN u2, count(s) AS shared ORDER BY shared DESC
        """
        user = self.users.get(user_id)
        if not user:
            return []
        user_skills = set(user.skills)
        similar = []
        for other in self.users.values():
            if other.id == user_id:
                continue
            shared = user_skills & set(other.skills)
            if shared:
                similar.append((other, len(shared), list(shared)))
        similar.sort(key=lambda x: x[1], reverse=True)
        return similar

    def get_recommendations(self, user_id: str):
        """
        Recommend users based on shared skills or common projects.
        TODO Neo4j: MATCH (u:User {id:$id})-[:TIENE_HABILIDAD]->(s)<-[:TIENE_HABILIDAD]-(rec)
                    WHERE NOT (u)-[:CONECTA_CON]-(rec) AND u <> rec
                    RETURN DISTINCT rec, count(s) AS score ORDER BY score DESC
        """
        user = self.users.get(user_id)
        if not user:
            return []
        connected_ids = {u.id for u in self.get_connections(user_id)} | {user_id}
        user_skills = set(user.skills)
        user_proj_ids = {p["project_id"] for p in self.participations if p["user_id"] == user_id}

        recs = []
        for uid, other in self.users.items():
            if uid in connected_ids:
                continue
            shared_skills = user_skills & set(other.skills)
            other_proj_ids = {p["project_id"] for p in self.participations if p["user_id"] == uid}
            shared_projects = user_proj_ids & other_proj_ids
            score = len(shared_skills) * 2 + len(shared_projects) * 3
            if score > 0:
                recs.append((other, score, list(shared_skills), list(shared_projects)))
        recs.sort(key=lambda x: x[1], reverse=True)
        return recs

    def get_shortest_path(self, start_id: str, end_id: str):
        """TODO Neo4j: MATCH path = shortestPath((a {id:$start})-[*]-(b {id:$end})) RETURN path"""
        from collections import deque
        adj = {}
        for c in self.connections:
            if c.status != "accepted":
                continue
            adj.setdefault(c.user_id_1, []).append(c.user_id_2)
            adj.setdefault(c.user_id_2, []).append(c.user_id_1)
        visited = {start_id}
        queue = deque([(start_id, [start_id])])
        while queue:
            current, path = queue.popleft()
            if current == end_id:
                return [self.users.get(uid) for uid in path if uid in self.users]
            for neighbor in adj.get(current, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        return []

    def get_network_graph_data(self):
        """Get nodes and edges for the visual network graph."""
        nodes = []
        for u in self.users.values():
            nodes.append({"id": u.id, "label": u.name, "type": "user", "color": u.avatar_color})
        for c in self.companies.values():
            nodes.append({"id": c.id, "label": c.name, "type": "company", "color": c.logo_color})
        edges = []
        for c in self.connections:
            if c.status == "accepted":
                edges.append({"from": c.user_id_1, "to": c.user_id_2, "type": "CONECTA_CON"})
        for w in self.works_at:
            if w.is_current:
                edges.append({"from": w.user_id, "to": w.company_id, "type": "TRABAJA_EN"})
        return {"nodes": nodes, "edges": edges}

    def get_skill_match_percent(self, user_id: str, job_id: str):
        """Calculate match % between user skills and job required skills."""
        user = self.users.get(user_id)
        job = self.jobs.get(job_id)
        if not user or not job or not job.required_skills:
            return 0
        user_skills = set(user.skills)
        job_skills = set(job.required_skills)
        return int(len(user_skills & job_skills) / len(job_skills) * 100)

    def close(self):
        """Close database connection. TODO Neo4j: self.driver.close()"""
        pass
