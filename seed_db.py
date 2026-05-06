import uuid
from datetime import datetime
from services.graph_service import GraphService
from models.models import User, Company, Project, JobOffer
from services.connection import get_driver, administra_empresa, trabaja_en

def reset_db():
    driver = get_driver()
    driver.execute_query("MATCH (n) DETACH DELETE n", database_="005fc815")
    print("Base de datos limpiada por completo.")

def seed():
    service = GraphService()
    
    # --- COMPANIES ---
    comp1 = Company(
        id=f"c_{uuid.uuid4().hex[:8]}", name="TechNova", description="Innovando el futuro del software.",
        industry="Tecnología", logo_color="#2563eb", location="Madrid, España",
        employee_count=1, founded_year=2020
    )
    comp2 = Company(
        id=f"c_{uuid.uuid4().hex[:8]}", name="DataCorp", description="Soluciones de Big Data e IA.",
        industry="Inteligencia Artificial", logo_color="#7c3aed", location="Bogotá, Colombia",
        employee_count=1, founded_year=2018
    )
    service.create_company(comp1)
    service.create_company(comp2)
    print("✓ Empresas creadas (TechNova, DataCorp)")

    # --- ADMINS ---
    admin1 = User(
        id="admin@technova.com", name="Laura Gómez", email="admin@technova.com", password="password123",
        title="Administrador / HR", avatar_color="#2563eb", location="Madrid, España",
        skills=["Scrum", "Agile", "Liderazgo"], is_online=True
    )
    admin2 = User(
        id="admin@datacorp.com", name="Carlos Restrepo", email="admin@datacorp.com", password="password123",
        title="Administrador / HR", avatar_color="#7c3aed", location="Bogotá, Colombia",
        skills=["Machine Learning", "Python"], is_online=False
    )
    service.create_user(admin1)
    service.create_user(admin2)
    
    # Conectar admins a empresas
    driver = get_driver()
    trabaja_en(driver, admin1.email, comp1.name)
    administra_empresa(driver, admin1.email, comp1.name)
    trabaja_en(driver, admin2.email, comp2.name)
    administra_empresa(driver, admin2.email, comp2.name)
    print("✓ Administradores creados y vinculados")

    # --- REGULAR USERS ---
    user1 = User(
        id="juan@gmail.com", name="Juan Pérez", email="juan@gmail.com", password="password123",
        title="Desarrollador Frontend", avatar_color="#10b981", location="Valencia, España",
        skills=["JavaScript", "React", "CSS", "HTML"], is_online=True
    )
    user2 = User(
        id="ana@hotmail.com", name="Ana Martínez", email="ana@hotmail.com", password="password123",
        title="Ingeniera de Datos", avatar_color="#f59e0b", location="Medellín, Colombia",
        skills=["Python", "SQL", "Machine Learning"], is_online=True
    )
    user3 = User(
        id="luis@dev.io", name="Luis Torres", email="luis@dev.io", password="password123",
        title="Backend Developer", avatar_color="#ef4444", location="Ciudad de México, México",
        skills=["Node.js", "Docker", "SQL"], is_online=False
    )
    service.create_user(user1)
    service.create_user(user2)
    service.create_user(user3)
    print("✓ Usuarios regulares creados (Juan, Ana, Luis)")

    # --- CONNECTIONS ---
    service.send_connection_request(user1.email, user2.email)
    service.send_connection_request(user2.email, user3.email)
    print("✓ Conexiones entre usuarios establecidas")

    # --- PROJECTS ---
    proj1 = Project(
        id=f"p_{uuid.uuid4().hex[:8]}", name="Sistema de Gestión Interna", company_id=comp1.id, company_name=comp1.name,
        description="Plataforma interna para gestión de empleados de TechNova.", status="Active",
        technologies=["React", "Node.js", "Docker"]
    )
    proj2 = Project(
        id=f"p_{uuid.uuid4().hex[:8]}", name="Motor de Recomendación", company_id=comp2.id, company_name=comp2.name,
        description="Sistema de IA para recomendar productos en e-commerce.", status="Active",
        technologies=["Python", "Machine Learning"]
    )
    service.create_project(proj1)
    service.create_project(proj2)
    print("✓ Proyectos publicados")

    # --- JOBS ---
    job1 = JobOffer(
        id=f"j_{uuid.uuid4().hex[:8]}", title="Frontend React Engineer", company_id=comp1.id, company_name=comp1.name,
        project_id=proj1.id, project_name=proj1.name, description="Desarrollo de UI en React para Sistema de Gestión.",
        location="Remoto", salary_range="$30k - $45k USD", job_type="Full-time",
        required_skills=["React", "JavaScript", "CSS"], posted_date=datetime.now().strftime("%Y-%m-%d"),
        experience_level="Mid-Senior"
    )
    job2 = JobOffer(
        id=f"j_{uuid.uuid4().hex[:8]}", title="Data Scientist", company_id=comp2.id, company_name=comp2.name,
        project_id=proj2.id, project_name=proj2.name, description="Creación de modelos predictivos para recomendaciones.",
        location="Híbrido", salary_range="$40k - $60k USD", job_type="Full-time",
        required_skills=["Python", "Machine Learning", "SQL"], posted_date=datetime.now().strftime("%Y-%m-%d"),
        experience_level="Senior"
    )
    service.create_job(job1)
    service.create_job(job2)
    print("✓ Vacantes creadas")

    # --- APPLICATIONS ---
    # Juan applies to Frontend job
    service.apply_to_job(user1.email, job1.title)
    # Ana applies to Data Scientist job
    service.apply_to_job(user2.email, job2.title)
    print("✓ Aplicaciones a vacantes simuladas")
    
    print("\n¡Sembrado de base de datos completado con éxito!")

if __name__ == "__main__":
    reset_db()
    seed()
