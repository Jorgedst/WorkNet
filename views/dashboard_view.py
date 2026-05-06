"""Dashboard view - Main view matching the ProNetwork design."""

import threading
import flet as ft
from utils.colors import (
    BG_PRIMARY, BG_INPUT, TEXT_PRIMARY, TEXT_SECONDARY,
    ACCENT_PRIMARY, ACCENT_SUCCESS, BORDER_COLOR, BG_CARD,
)
from components.user_card import user_card
from components.network_graph import network_graph
from services.graph_service import GraphService, PREDEFINED_SKILLS
from utils.colors import get_skill_color


def _skeleton_box(width=None, height=16, radius=8):
    """Animated placeholder block."""
    return ft.Container(
        width=width,
        height=height,
        bgcolor="#1e2444",
        border_radius=radius,
        animate_opacity=ft.Animation(800, ft.AnimationCurve.EASE_IN_OUT),
    )


def _skeleton_loader():
    """Full-page skeleton shown while data loads."""
    def row(*widths, h=14):
        return ft.Row(
            controls=[_skeleton_box(width=w, height=h) for w in widths],
            spacing=12,
        )

    return ft.Column(
        controls=[
            # Header skeleton
            ft.Row(controls=[_skeleton_box(width=160, height=28), _skeleton_box(height=40)],
                   vertical_alignment=ft.CrossAxisAlignment.CENTER, spacing=16),
            ft.Container(height=20),
            # Card rows skeleton
            *[ft.Row(controls=[
                ft.Container(
                    content=ft.Column(controls=[
                        _skeleton_box(height=20, radius=10),
                        ft.Container(height=8),
                        _skeleton_box(width=120, height=13),
                        ft.Container(height=6),
                        row(60, 70, 50, h=12),
                    ], spacing=4),
                    bgcolor="#141828",
                    border_radius=14,
                    padding=16,
                    expand=True,
                    border=ft.border.all(1, BORDER_COLOR),
                ),
                ft.Container(
                    content=ft.Column(controls=[
                        _skeleton_box(height=20, radius=10),
                        ft.Container(height=8),
                        _skeleton_box(width=100, height=13),
                        ft.Container(height=6),
                        row(55, 65, 45, h=12),
                    ], spacing=4),
                    bgcolor="#141828",
                    border_radius=14,
                    padding=16,
                    expand=True,
                    border=ft.border.all(1, BORDER_COLOR),
                ),
            ], spacing=12) for _ in range(3)],
        ],
        spacing=12,
        expand=True,
    )


def dashboard_content(page: ft.Page, on_view_profile=None):
    """Build the dashboard content area — data loads in a background thread."""
    service = GraphService()

    # Shared mutable state set once data is loaded
    _state = {"all_users": [], "cards_col_ref": None}

    def _build_cards_column(users):
        card_rows = []
        for i in range(0, len(users), 2):
            row_cards = []
            for j in range(2):
                if i + j < len(users):
                    row_cards.append(user_card(users[i + j], on_view_profile=on_view_profile, show_connect=False))
                else:
                    row_cards.append(ft.Container(expand=True))
            card_rows.append(ft.Row(controls=row_cards, spacing=12))
        return card_rows

    def _on_search(e):
        query = (e.control.value or "").strip().lower()
        users = _state["all_users"]
        if query:
            users = [
                u for u in users
                if query in u.name.lower()
                or query in (u.title or "").lower()
                or any(query in s.lower() for s in (u.skills or []))
            ]
        col = _state["cards_col_ref"]
        if col is not None:
            col.controls = _build_cards_column(users)
            try:
                col.update()
            except Exception:
                pass

    # ── Search bar (render immediately) ──────────────────────────────────────
    search_bar = ft.TextField(
        hint_text="Buscar por nombre, cargo o habilidad...",
        prefix_icon=ft.Icons.SEARCH_ROUNDED,
        border_color=BORDER_COLOR,
        focused_border_color=ACCENT_PRIMARY,
        bgcolor=BG_INPUT,
        color=TEXT_PRIMARY,
        hint_style=ft.TextStyle(color=TEXT_SECONDARY),
        cursor_color=ACCENT_PRIMARY,
        border_radius=12,
        height=44,
        text_size=14,
        expand=True,
        on_change=_on_search,
    )

    header = ft.Row(
        controls=[
            ft.Text("Dashboard", color=TEXT_PRIMARY, size=24, weight=ft.FontWeight.BOLD),
            ft.Container(width=16),
            search_bar,
        ],
        alignment=ft.MainAxisAlignment.START,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    # ── Content container: starts with skeleton ───────────────────────────────
    content_area = ft.Container(content=_skeleton_loader(), expand=True)
    graph_area   = ft.Container(content=_skeleton_box(height=400, radius=16), expand=True)

    layout = ft.Column(
        controls=[
            ft.Container(content=header, padding=ft.padding.only(bottom=16)),
            ft.Row(
                controls=[
                    ft.Container(content=content_area, expand=3),
                    ft.Container(content=graph_area,   expand=2),
                ],
                spacing=16,
                expand=True,
                vertical_alignment=ft.CrossAxisAlignment.START,
            ),
        ],
        expand=True,
        spacing=0,
    )

    # ── Background loader ─────────────────────────────────────────────────────
    import time
    def _load_data():
        time.sleep(0.05)
        try:
            current_user  = service.get_current_user()
            admin_company = service.get_admin_company(current_user.id)
            all_users     = [u for u in service.get_all_users() if u.id != current_user.id]
            my_apps       = service.get_user_applications(current_user.id)
            applied_jobs  = [service.get_job(jid) for jid in my_apps if service.get_job(jid)]
        except Exception:
            return

        # ── Build real UI components ──────────────────────────────────────────
        def on_connect(uid):
            service.send_connection_request(current_user.id, uid)
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Solicitud de conexión enviada", color=TEXT_PRIMARY),
                bgcolor="#1e2444",
            )
            page.snack_bar.open = True
            page.update()

        # Store for search filtering
        _state["all_users"] = all_users

        # Cards grid
        cards_column = ft.Column(controls=_build_cards_column(all_users), spacing=12)
        _state["cards_col_ref"] = cards_column

        # ── Company admin branch ──────────────────────────────────────────────
        if admin_company:
            from models.models import Project, JobOffer

            def create_project_dialog(e):
                name_field = ft.TextField(label="Nombre del Proyecto", bgcolor=BG_INPUT,
                                          border_color=BORDER_COLOR, color=TEXT_PRIMARY)
                desc_field = ft.TextField(label="Descripción", multiline=True, bgcolor=BG_INPUT,
                                          border_color=BORDER_COLOR, color=TEXT_PRIMARY)
                selected_skills = set()
                skills_container = ft.Row(wrap=True, spacing=6, run_spacing=6)

                def toggle_skill(name):
                    if name in selected_skills: selected_skills.remove(name)
                    else: selected_skills.add(name)
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

                def save(e):
                    import uuid
                    p = Project(id=f"p_{uuid.uuid4().hex[:8]}", name=name_field.value,
                                company_id=admin_company.id, company_name=admin_company.name,
                                description=desc_field.value, status="Active",
                                technologies=list(selected_skills))
                    service.create_project(p)
                    dlg.open = False
                    page.run_task(page.push_route, page.route)

                dlg = ft.AlertDialog(
                    title=ft.Text("Nuevo Proyecto", color=TEXT_PRIMARY),
                    content=ft.Column([name_field, desc_field,
                                       ft.Text("Habilidades/Tecnologías:", color=TEXT_PRIMARY),
                                       skills_container], tight=True),
                    bgcolor=BG_CARD,
                    actions=[
                        ft.TextButton("Cancelar", on_click=lambda e: (setattr(dlg, "open", False), page.update())),
                        ft.TextButton("Guardar", on_click=save, style=ft.ButtonStyle(color=ACCENT_PRIMARY)),
                    ],
                )
                page.overlay.append(dlg)
                dlg.open = True
                page.update()

            def create_vacancy_dialog(e, project):
                title_field = ft.TextField(label="Título de Vacante", bgcolor=BG_INPUT,
                                           border_color=BORDER_COLOR, color=TEXT_PRIMARY)
                loc_field = ft.TextField(label="Modalidad (Remoto, Presencial, Híbrido)", bgcolor=BG_INPUT,
                                         border_color=BORDER_COLOR, color=TEXT_PRIMARY)
                selected_skills = set()
                skills_container = ft.Row(wrap=True, spacing=6, run_spacing=6)

                def toggle_skill(name):
                    if name in selected_skills: selected_skills.remove(name)
                    else: selected_skills.add(name)
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

                def save(e):
                    import uuid
                    from datetime import datetime
                    new_job = JobOffer(
                        id=f"j_{uuid.uuid4().hex[:8]}", title=title_field.value,
                        company_id=admin_company.id, company_name=admin_company.name,
                        project_id=project.id, project_name=project.name,
                        description="Vacante.", location=loc_field.value,
                        salary_range="A convenir", job_type="Full-time",
                        required_skills=list(selected_skills),
                        posted_date=datetime.now().strftime("%Y-%m-%d"),
                        experience_level="Cualquiera",
                    )
                    service.create_job(new_job)
                    dlg.open = False
                    page.run_task(page.push_route, page.route)

                dlg = ft.AlertDialog(
                    title=ft.Text(f"Nueva Vacante en {project.name}", color=TEXT_PRIMARY),
                    content=ft.Column([title_field, loc_field,
                                       ft.Text("Habilidades Requeridas:", color=TEXT_PRIMARY),
                                       skills_container], tight=True),
                    bgcolor=BG_CARD,
                    actions=[
                        ft.TextButton("Cancelar", on_click=lambda e: (setattr(dlg, "open", False), page.update())),
                        ft.TextButton("Guardar", on_click=save, style=ft.ButtonStyle(color=ACCENT_PRIMARY)),
                    ],
                )
                page.overlay.append(dlg)
                dlg.open = True
                page.update()

            company_projects = service.get_company_projects(admin_company.id)
            projects_items = []
            for p in company_projects:
                vacs = service.get_project_jobs(p.id)
                projects_items.append(ft.Container(
                    content=ft.Row(controls=[
                        ft.Icon(ft.Icons.FOLDER_ROUNDED, color=ACCENT_PRIMARY, size=18),
                        ft.Column(controls=[
                            ft.Text(p.name, color=TEXT_PRIMARY, size=14, weight=ft.FontWeight.W_600),
                            ft.Text(f"{len(vacs)} vacantes", color=TEXT_SECONDARY, size=12),
                        ], spacing=2, expand=True),
                        ft.Container(
                            content=ft.Text("+ Nueva Vacante", color=TEXT_PRIMARY, size=11),
                            bgcolor="#1e2444", border_radius=6,
                            padding=ft.padding.symmetric(horizontal=10, vertical=4),
                            on_click=lambda e, p_ref=p: create_vacancy_dialog(e, p_ref), ink=True,
                        ),
                        ft.Container(width=4),
                        ft.Container(
                            content=ft.Text(p.status, color=ACCENT_SUCCESS, size=12, weight=ft.FontWeight.W_500),
                            bgcolor=ACCENT_SUCCESS + "20", border_radius=8,
                            padding=ft.padding.symmetric(horizontal=10, vertical=4),
                        ),
                    ]),
                    bgcolor=BG_PRIMARY, border_radius=10, border=ft.border.all(1, BORDER_COLOR), padding=12,
                ))

            left_col = ft.Column(
                controls=[
                    ft.Text(f"Dashboard - {admin_company.name}", color=TEXT_PRIMARY, size=20,
                            weight=ft.FontWeight.BOLD),
                    ft.Container(height=16),
                    ft.Row(controls=[
                        ft.Text("Proyectos Publicados", color=TEXT_PRIMARY, size=18,
                                weight=ft.FontWeight.W_600),
                        ft.Container(expand=True),
                        ft.Container(
                            content=ft.Text("+ Nuevo Proyecto", color=TEXT_PRIMARY, size=12,
                                            weight=ft.FontWeight.W_500),
                            bgcolor=ACCENT_PRIMARY, border_radius=8,
                            padding=ft.padding.symmetric(horizontal=12, vertical=6),
                            on_click=create_project_dialog, ink=True,
                        ),
                    ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    ft.Container(height=8),
                    ft.Column(controls=projects_items, spacing=8) if projects_items
                    else ft.Text("No hay proyectos.", color=TEXT_SECONDARY),
                ],
                spacing=0, scroll=ft.ScrollMode.AUTO, expand=True,
            )

        else:
            # ── Regular user branch ───────────────────────────────────────────
            applied_items = []
            for job in applied_jobs:
                applied_items.append(ft.Container(
                    content=ft.Row(controls=[
                        ft.Icon(ft.Icons.WORK_ROUNDED, color=ACCENT_PRIMARY, size=18),
                        ft.Column(controls=[
                            ft.Text(job.title, color=TEXT_PRIMARY, size=14, weight=ft.FontWeight.W_600),
                            ft.Text(job.company_name, color=TEXT_SECONDARY, size=12),
                        ], spacing=2, expand=True),
                        ft.Container(
                            content=ft.Text("Aplicado", color=ACCENT_SUCCESS, size=12,
                                            weight=ft.FontWeight.W_500),
                            bgcolor=ACCENT_SUCCESS + "20", border_radius=8,
                            padding=ft.padding.symmetric(horizontal=10, vertical=4),
                        ),
                    ]),
                    bgcolor=BG_PRIMARY, border_radius=10, border=ft.border.all(1, BORDER_COLOR), padding=12,
                ))

            applied_section = ft.Column(controls=[
                ft.Text("Mis Aplicaciones", color=TEXT_PRIMARY, size=18, weight=ft.FontWeight.W_600),
                ft.Container(height=4),
                ft.Column(controls=applied_items, spacing=8),
                ft.Container(height=16),
            ]) if applied_items else ft.Container()

            left_col = ft.Column(
                controls=[
                    applied_section,
                    ft.Text("Sugerencias de Red", color=TEXT_PRIMARY, size=18, weight=ft.FontWeight.W_600),
                    ft.Container(height=4),
                    cards_column,
                ],
                spacing=0, scroll=ft.ScrollMode.AUTO, expand=True,
            )

        graph_container = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Grafo Visual de Red", color=TEXT_PRIMARY, size=16,
                            weight=ft.FontWeight.W_600),
                    ft.Container(
                        content=ft.ProgressRing(color=ACCENT_PRIMARY, width=32, height=32),
                        alignment=ft.Alignment(0, 0),
                        expand=True,
                    ),
                ],
                spacing=8,
            ),
            bgcolor=BG_CARD,
            border_radius=16,
            border=ft.border.all(1, BORDER_COLOR),
            padding=16,
            expand=True,
        )

        def _load_graph():
            try:
                graph_data = service.get_network_graph_data()
                panel = network_graph(
                    graph_data,
                    on_node_click=lambda n: on_view_profile(n["id"]) if on_view_profile and n["type"] == "user" else None,
                )
                graph_container.content = panel.content
                graph_container.update()
            except Exception:
                pass

        threading.Thread(target=_load_graph, daemon=True).start()
        graph_panel = graph_container 

        # ── Swap skeleton → real content ──────────────────────────────────────
        content_area.content = left_col
        graph_area.content   = graph_panel
        try:
            content_area.update()
        except Exception:
            pass
        try:
            graph_area.update()
            page.update()
        except Exception:
            pass

    page.run_thread(_load_data)
    return layout
