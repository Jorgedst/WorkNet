"""Company register page view - Register a company with a project and a vacancy."""

import flet as ft
from utils.colors import (
    BG_PRIMARY, BG_SECONDARY, BG_INPUT, TEXT_PRIMARY, TEXT_SECONDARY,
    ACCENT_PRIMARY, ACCENT_DANGER, BORDER_COLOR, GRADIENT_START, GRADIENT_END,
    BG_CARD,
)
from services.graph_service import GraphService, PREDEFINED_SKILLS
from models.models import User, Company, Project, JobOffer, WorksAt
from utils.colors import get_skill_color

def company_register_view(page: ft.Page):
    """Build company registration page."""
    service = GraphService()
    error_text = ft.Text("", color=ACCENT_DANGER, size=12, visible=False)

    def _field(label, hint, icon, password=False):
        return ft.TextField(
            label=label, hint_text=hint, prefix_icon=icon,
            password=password, can_reveal_password=password,
            border_color=BORDER_COLOR, focused_border_color=ACCENT_PRIMARY,
            bgcolor=BG_INPUT, color=TEXT_PRIMARY,
            label_style=ft.TextStyle(color=TEXT_SECONDARY),
            hint_style=ft.TextStyle(color=TEXT_SECONDARY),
            cursor_color=ACCENT_PRIMARY, border_radius=12, height=50, text_size=13,
        )

    # Company fields
    c_name = _field("Nombre de la Empresa", "Ej. TechCorp", ft.Icons.BUSINESS_ROUNDED)
    c_ind = _field("Industria", "Ej. Tecnología, IA...", ft.Icons.FACTORY_ROUNDED)
    c_loc = _field("Ubicación", "Ej. Madrid, España", ft.Icons.LOCATION_ON_ROUNDED)
    
    # First project and job fields
    p_name = _field("Nombre de tu primer Proyecto", "Ej. Nueva App Móvil", ft.Icons.FOLDER_ROUNDED)
    j_title = _field("Título de tu primera Vacante", "Ej. Frontend Developer", ft.Icons.WORK_ROUNDED)
    
    # ── Skill selector for the first vacancy ──────────────────────────────────
    selected_skills = set()
    skills_container = ft.Row(wrap=True, spacing=6, run_spacing=6)

    def toggle_skill(name):
        if name in selected_skills:
            selected_skills.remove(name)
        else:
            selected_skills.add(name)
        skills_container.controls = [_skill_chip(s) for s in PREDEFINED_SKILLS]
        skills_container.update()

    def _skill_chip(name):
        sel = name in selected_skills
        colors = get_skill_color(name)
        return ft.Container(
            content=ft.Text(name, color=TEXT_PRIMARY if sel else colors["text"],
                            size=11, weight=ft.FontWeight.W_500),
            bgcolor=ACCENT_PRIMARY if sel else colors["bg"],
            border=ft.border.all(1, ACCENT_PRIMARY if sel else colors["border"]),
            border_radius=8,
            padding=ft.padding.symmetric(horizontal=10, vertical=5),
            on_click=lambda e, s=name: toggle_skill(s),
            animate=ft.Animation(150, ft.AnimationCurve.EASE_IN_OUT),
        )

    skills_container.controls = [_skill_chip(s) for s in PREDEFINED_SKILLS]

    # Admin User credentials
    u_email = _field("Correo del Administrador", "admin@empresa.com", ft.Icons.EMAIL_ROUNDED)
    u_pass = _field("Contraseña", "••••••••", ft.Icons.LOCK_ROUNDED, password=True)

    def do_register(e):
        if not (c_name.value and c_ind.value and c_loc.value and 
                p_name.value and j_title.value and u_email.value and u_pass.value):
            error_text.value = "Todos los campos son obligatorios."
            error_text.visible = True
            page.update()
            return

        if not selected_skills:
            error_text.value = "Selecciona al menos una habilidad requerida para la vacante."
            error_text.visible = True
            page.update()
            return
            
        import uuid
        from datetime import datetime
        
        c_id = f"c_{uuid.uuid4().hex[:8]}"
        u_id = u_email.value
        p_id = f"p_{uuid.uuid4().hex[:8]}"
        j_id = f"j_{uuid.uuid4().hex[:8]}"
        
        # 1. Company
        new_company = Company(id=c_id, name=c_name.value, description="Una nueva empresa en WorkNet.",
                              industry=c_ind.value, logo_color="#4f46e5", location=c_loc.value, 
                              employee_count=1, founded_year=datetime.now().year)
        service.create_company(new_company)
        
        # 2. Admin User
        new_user = User(id=u_id, name=f"Admin {c_name.value}", email=u_email.value, password=u_pass.value,
                        title="Administrador / HR", avatar_color="#4f46e5", location=c_loc.value,
                        skills=[], is_online=True)
        service.create_user(new_user)
        
        # 3. WorksAt and Admin relations in Neo4j (this explicitly associates admin email → company)
        from services.connection import get_driver, trabaja_en, administra_empresa
        driver = get_driver()
        trabaja_en(driver, u_email.value, c_name.value)
        administra_empresa(driver, u_email.value, c_name.value)
        
        # 4. Project
        new_proj = Project(id=p_id, name=p_name.value, company_id=c_id, company_name=c_name.value,
                           description="Primer proyecto registrado.", status="Active", technologies=list(selected_skills))
        service.create_project(new_proj)
        
        # 5. Vacancy — now with selected skills
        new_job = JobOffer(id=j_id, title=j_title.value, company_id=c_id, company_name=c_name.value,
                           project_id=p_id, project_name=p_name.value, description="Vacante inicial.",
                           location=c_loc.value, salary_range="A convenir", job_type="Full-time",
                           required_skills=list(selected_skills),
                           posted_date=datetime.now().strftime("%Y-%m-%d"), experience_level="Cualquiera")
        service.create_job(new_job)
        
        # 6. Login as admin — set session AND cache the admin company
        service.current_user_id = u_id
        service._current_user_obj = new_user   # cache user
        service._admin_company_obj = None       # reset so it re-fetches from DB on next call
        service._invalidate_cache()             # clear all caches for fresh data
        
        # Redirect to dashboard — will now show admin dashboard
        page.run_task(page.push_route, "/app/dashboard")

    # Layout
    main_container = ft.Container(
        content=ft.Container(
            content=ft.Column(
                controls=[
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Container(
                                    content=ft.Icon(ft.Icons.BUSINESS_ROUNDED, color=TEXT_PRIMARY, size=24),
                                    bgcolor=ACCENT_PRIMARY, border_radius=12, padding=8,
                                ),
                                ft.Text("Registrar Empresa", color=TEXT_PRIMARY, size=24, weight=ft.FontWeight.BOLD),
                            ],
                            spacing=12, alignment=ft.MainAxisAlignment.CENTER,
                        ),
                    ),
                    ft.Text("Únete a WorkNet y publica tus proyectos y vacantes", color=TEXT_SECONDARY, size=13, text_align=ft.TextAlign.CENTER),
                    ft.Container(height=10),
                    # ── Company info ──
                    ft.Text("Datos de la Empresa", color=ACCENT_PRIMARY, size=14, weight=ft.FontWeight.W_600),
                    c_name, c_ind, c_loc,
                    ft.Divider(color=BORDER_COLOR),
                    # ── First project ──
                    ft.Text("Primer Proyecto", color=ACCENT_PRIMARY, size=14, weight=ft.FontWeight.W_600),
                    p_name,
                    ft.Divider(color=BORDER_COLOR),
                    # ── First vacancy with skills ──
                    ft.Text("Primera Vacante", color=ACCENT_PRIMARY, size=14, weight=ft.FontWeight.W_600),
                    j_title,
                    ft.Container(height=4),
                    ft.Text("Habilidades requeridas para la vacante:", color=TEXT_PRIMARY, size=13),
                    ft.Container(
                        content=skills_container,
                        padding=ft.padding.symmetric(vertical=8),
                    ),
                    ft.Divider(color=BORDER_COLOR),
                    # ── Admin credentials ──
                    ft.Text("Credenciales del Administrador", color=ACCENT_PRIMARY, size=14, weight=ft.FontWeight.W_600),
                    u_email, u_pass,
                    error_text,
                    ft.Container(height=10),
                    ft.Container(
                        content=ft.Text("Registrar y Entrar", color=TEXT_PRIMARY, size=14, weight=ft.FontWeight.W_600),
                        bgcolor=ACCENT_PRIMARY, border_radius=12, padding=ft.padding.symmetric(vertical=14),
                        width=400, alignment=ft.Alignment(0, 0), on_click=do_register, ink=True,
                    ),
                    ft.Container(
                        content=ft.Text("Volver al Login", color=TEXT_SECONDARY, size=13),
                        on_click=lambda e: page.run_task(page.push_route, "/login"), ink=True,
                        padding=ft.padding.symmetric(vertical=10), alignment=ft.Alignment(0, 0),
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8,
                scroll=ft.ScrollMode.AUTO,
            ),
            width=520, bgcolor=BG_SECONDARY, border_radius=20, border=ft.border.all(1, BORDER_COLOR), padding=40,
            height=700,
        ),
        alignment=ft.Alignment(0, 0),
        expand=True,
        bgcolor=BG_PRIMARY,
        padding=20,
    )

    return ft.View(
        route="/register-company",
        controls=[main_container],
        bgcolor=BG_PRIMARY,
        padding=0,
        spacing=0,
    )
