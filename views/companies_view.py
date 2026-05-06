"""Companies view - Browse companies. Click shows projects, then vacancies."""

import threading
import flet as ft
from utils.colors import (
    BG_CARD, BG_INPUT, BG_PRIMARY, TEXT_PRIMARY, TEXT_SECONDARY,
    ACCENT_PRIMARY, ACCENT_SUCCESS, BORDER_COLOR,
)
from components.skill_tag import skill_tag
from services.graph_service import GraphService


def _skel(width=None, height=14, radius=8):
    return ft.Container(width=width, height=height, bgcolor="#1e2444", border_radius=radius)


def _skeleton_loader():
    """Skeleton grid of company cards."""
    def card_skel():
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(controls=[
                        ft.Container(width=52, height=52, bgcolor="#1e2444", border_radius=26),
                        ft.Column(controls=[
                            _skel(width=140, height=16),
                            _skel(width=90, height=12),
                        ], spacing=6, expand=True),
                        _skel(width=80, height=22, radius=20),
                    ], spacing=14),
                    _skel(height=12),
                    _skel(width=200, height=12),
                    ft.Row(controls=[_skel(w, 12) for w in (70, 90, 75)], spacing=8),
                ],
                spacing=10,
            ),
            bgcolor=BG_CARD, border_radius=14,
            border=ft.border.all(1, BORDER_COLOR), padding=20,
        )

    rows = []
    for _ in range(3):
        rows.append(ft.Row(controls=[
            ft.Container(content=card_skel(), expand=True),
            ft.Container(content=card_skel(), expand=True),
        ], spacing=12))

    return ft.Column(controls=rows, spacing=12)


def companies_content(page: ft.Page, on_view_profile=None):
    """Build the companies view — data loads in a background thread."""
    service = GraphService()

    # Shared mutable state
    _state = {"all_companies": [], "card_builder": None}

    def _build_grid(companies):
        rows = []
        build = _state["card_builder"]
        if build is None:
            return ft.Text("Cargando...", color=TEXT_SECONDARY)
        for i in range(0, len(companies), 2):
            row_items = [build(companies[i])]
            if i + 1 < len(companies):
                row_items.append(build(companies[i + 1]))
            else:
                row_items.append(ft.Container(expand=True))
            rows.append(ft.Row(
                controls=[ft.Container(content=c, expand=True) for c in row_items],
                spacing=12,
            ))
        return ft.Column(controls=rows, spacing=12) if rows else ft.Text(
            "Sin resultados.", color=TEXT_SECONDARY
        )

    def _on_search(e):
        query = (e.control.value or "").strip().lower()
        companies = _state["all_companies"]
        if _state["card_builder"] is None:
            return
        if query:
            companies = [
                c for c in companies
                if query in c.name.lower()
                or query in (c.industry or "").lower()
                or query in (c.location or "").lower()
            ]
        grid_container.content = _build_grid(companies)
        try:
            grid_container.update()
        except Exception:
            pass

    # ── Header (rendered immediately) ─────────────────────────────────────────
    header = ft.Row(
        controls=[
            ft.Text("Empresas", color=TEXT_PRIMARY, size=24, weight=ft.FontWeight.BOLD),
            ft.Container(expand=True),
            ft.TextField(
                hint_text="Buscar por nombre, sector o ciudad...",
                prefix_icon=ft.Icons.SEARCH_ROUNDED,
                border_color=BORDER_COLOR, focused_border_color=ACCENT_PRIMARY,
                bgcolor=BG_INPUT, color=TEXT_PRIMARY, hint_style=ft.TextStyle(color=TEXT_SECONDARY),
                cursor_color=ACCENT_PRIMARY, border_radius=12, height=42, text_size=13, width=300,
                on_change=_on_search,
            ),
        ],
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    grid_container = ft.Container(content=_skeleton_loader(), expand=True)

    layout = ft.Column(
        controls=[header, ft.Container(height=12), grid_container],
        spacing=0, scroll=ft.ScrollMode.AUTO, expand=True,
    )

    # ── Background loader ─────────────────────────────────────────────────────
    def _load_data():
        try:
            current_user = service.get_current_user()
            companies    = service.get_all_companies()
            all_projects = service.get_all_projects()
            all_jobs     = service.get_all_jobs()

            # Pre-fetch projects and jobs for all companies using entirely in-memory data
            company_projects_cache = {}
            company_jobs_cache = {}
            for c in companies:
                # Projects for this company
                c_projs = [p for p in all_projects if p.company_name == c.name]
                company_projects_cache[c.id] = c_projs
                
                # Total jobs for this company
                c_jobs = [j for j in all_jobs if j.company_name == c.name]
                company_jobs_cache[c.id] = len(c_jobs)

        except Exception:
            return

        # ── Dialog helpers ────────────────────────────────────────────────────
        def show_project_vacancies(project):
            vacancies = service.get_project_jobs(project.id)

            def apply_to_job(e, job_id):
                service.apply_to_job(current_user.id, job_id)
                e.control.content.value = "Aplicado"
                e.control.content.color = ACCENT_SUCCESS
                e.control.bgcolor = ACCENT_SUCCESS + "20"
                e.control.on_click = None
                success_dlg = ft.AlertDialog(
                    title=ft.Text("¡Aplicación exitosa!", color=TEXT_PRIMARY),
                    content=ft.Text("Tu aplicación ha sido enviada correctamente.", color=TEXT_SECONDARY),
                    bgcolor=BG_CARD,
                    actions=[ft.Container(
                        content=ft.Text("Aceptar", color=TEXT_PRIMARY, size=13),
                        bgcolor=ACCENT_PRIMARY, border_radius=8,
                        padding=ft.padding.symmetric(horizontal=20, vertical=8),
                        on_click=lambda e: (setattr(success_dlg, "open", False), page.update()), ink=True,
                    )],
                )
                page.dialog = success_dlg
                success_dlg.open = True
                page.update()

            items = []
            if vacancies:
                for job in vacancies:
                    match = service.get_skill_match_percent(current_user.id, job.id)
                    match_color = ACCENT_SUCCESS if match >= 60 else "#f59e0b" if match >= 30 else TEXT_SECONDARY
                    has_applied = service.has_applied(current_user.id, job.id)
                    items.append(ft.Container(
                        content=ft.Row(controls=[
                            ft.Column(controls=[
                                ft.Text(job.title, color=TEXT_PRIMARY, size=14, weight=ft.FontWeight.W_600),
                                ft.Row(controls=[
                                    ft.Text(job.location, color=TEXT_SECONDARY, size=11),
                                    ft.Text("•", color=TEXT_SECONDARY),
                                    ft.Text(job.salary_range, color=ACCENT_SUCCESS, size=11),
                                ], spacing=6),
                                ft.Row(controls=[skill_tag(s) for s in job.required_skills[:4]], spacing=4),
                            ], spacing=4, expand=True),
                            ft.Column(controls=[
                                ft.Text(f"{match}%", color=match_color, size=16, weight=ft.FontWeight.BOLD),
                                ft.Container(
                                    content=ft.Text("Aplicado" if has_applied else "Aplicar",
                                                    color=TEXT_PRIMARY if not has_applied else ACCENT_SUCCESS,
                                                    size=12),
                                    bgcolor=ACCENT_PRIMARY if not has_applied else ACCENT_SUCCESS + "20",
                                    border_radius=8,
                                    padding=ft.padding.symmetric(horizontal=12, vertical=6),
                                    on_click=(lambda e, jid=job.id: apply_to_job(e, jid)) if not has_applied else None,
                                    ink=True,
                                ),
                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
                        ]),
                        bgcolor=BG_PRIMARY, border_radius=10,
                        border=ft.border.all(1, BORDER_COLOR), padding=12,
                    ))
            else:
                items.append(ft.Text("No hay vacantes en este proyecto", color=TEXT_SECONDARY))

            dlg = ft.AlertDialog(
                title=ft.Text(f"Vacantes - {project.name}", color=TEXT_PRIMARY, size=16,
                              weight=ft.FontWeight.W_600),
                content=ft.Container(
                    content=ft.Column(controls=items, spacing=8, scroll=ft.ScrollMode.AUTO),
                    width=500, height=350,
                ),
                bgcolor=BG_CARD,
                actions=[ft.Container(
                    content=ft.Text("Cerrar", color=TEXT_SECONDARY, size=13),
                    border=ft.border.all(1, BORDER_COLOR), border_radius=8,
                    padding=ft.padding.symmetric(horizontal=20, vertical=8),
                    on_click=lambda e: (setattr(dlg, "open", False), page.update()), ink=True,
                )],
            )
            page.dialog = dlg
            dlg.open = True
            page.update()

        def show_company_projects(company):
            projects = company_projects_cache.get(company.id, [])
            project_items = []
            if projects:
                for proj in projects:
                    vacancies = service.get_project_jobs(proj.id)
                    status_colors = {"Active": ACCENT_SUCCESS, "Completed": ACCENT_PRIMARY, "On Hold": "#f59e0b"}
                    status_map    = {"Active": "Activo", "Completed": "Completado", "On Hold": "En pausa"}
                    color = status_colors.get(proj.status, TEXT_SECONDARY)

                    project_items.append(ft.Container(
                        content=ft.Column(controls=[
                            ft.Row(controls=[
                                ft.Icon(ft.Icons.FOLDER_ROUNDED, color=ACCENT_PRIMARY, size=18),
                                ft.Text(proj.name, color=TEXT_PRIMARY, size=14,
                                        weight=ft.FontWeight.W_600, expand=True),
                                ft.Container(
                                    content=ft.Text(status_map.get(proj.status, proj.status), color=color, size=10),
                                    bgcolor=color + "20", border_radius=20,
                                    padding=ft.padding.symmetric(horizontal=10, vertical=3),
                                ),
                            ], spacing=8),
                            ft.Text(proj.description, color=TEXT_SECONDARY, size=12, max_lines=2,
                                    overflow=ft.TextOverflow.ELLIPSIS),
                            ft.Row(controls=[skill_tag(t) for t in proj.technologies[:4]], spacing=4),
                            ft.Row(controls=[
                                ft.Text(f"{len(vacancies)} vacantes", color=TEXT_SECONDARY, size=11),
                                ft.Container(expand=True),
                                ft.Container(
                                    content=ft.Text("Ver Vacantes", color=TEXT_PRIMARY, size=11,
                                                    weight=ft.FontWeight.W_500),
                                    bgcolor=ACCENT_PRIMARY, border_radius=6,
                                    padding=ft.padding.symmetric(horizontal=12, vertical=5),
                                    on_click=lambda e, p=proj: (setattr(dlg, "open", False), page.update(),
                                                                 show_project_vacancies(p)),
                                    ink=True,
                                ),
                            ]),
                        ], spacing=6),
                        bgcolor=BG_PRIMARY, border_radius=10,
                        border=ft.border.all(1, BORDER_COLOR), padding=14,
                    ))
            else:
                project_items.append(ft.Text("No hay proyectos registrados", color=TEXT_SECONDARY))

            dlg = ft.AlertDialog(
                title=ft.Row(controls=[
                    ft.CircleAvatar(
                        content=ft.Text(company.initials, size=14, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                        bgcolor=company.logo_color, radius=18,
                    ),
                    ft.Text(f"Proyectos de {company.name}", color=TEXT_PRIMARY, size=16,
                            weight=ft.FontWeight.W_600),
                ], spacing=10),
                content=ft.Container(
                    content=ft.Column(controls=project_items, spacing=10, scroll=ft.ScrollMode.AUTO),
                    width=520, height=400,
                ),
                bgcolor=BG_CARD,
                actions=[ft.Container(
                    content=ft.Text("Cerrar", color=TEXT_SECONDARY, size=13),
                    border=ft.border.all(1, BORDER_COLOR), border_radius=8,
                    padding=ft.padding.symmetric(horizontal=20, vertical=8),
                    on_click=lambda e: (setattr(dlg, "open", False), page.update()), ink=True,
                )],
            )
            page.dialog = dlg
            dlg.open = True
            page.update()

        # ── Build company cards ───────────────────────────────────────────────
        def company_card(company):
            projs      = company_projects_cache.get(company.id, [])
            total_jobs = company_jobs_cache.get(company.id, 0)
            emp_count  = company.employee_count

            return ft.Container(
                content=ft.Column(controls=[
                    ft.Row(controls=[
                        ft.CircleAvatar(
                            content=ft.Text(company.initials, size=18, weight=ft.FontWeight.BOLD,
                                            color=TEXT_PRIMARY),
                            bgcolor=company.logo_color, radius=26,
                        ),
                        ft.Column(controls=[
                            ft.Text(company.name, color=TEXT_PRIMARY, size=16, weight=ft.FontWeight.W_600),
                            ft.Text(company.industry, color=ACCENT_PRIMARY, size=12),
                        ], spacing=2, expand=True),
                        ft.Container(
                            content=ft.Text(f"{len(projs)} proyectos", color=ACCENT_PRIMARY, size=12),
                            bgcolor=ACCENT_PRIMARY + "20", border_radius=20,
                            padding=ft.padding.symmetric(horizontal=12, vertical=4),
                        ),
                    ], spacing=14),
                    ft.Text(company.description, color=TEXT_SECONDARY, size=13, max_lines=2,
                            overflow=ft.TextOverflow.ELLIPSIS),
                    ft.Container(height=4),
                    ft.Row(controls=[
                        ft.Icon(ft.Icons.LOCATION_ON_ROUNDED, color=TEXT_SECONDARY, size=14),
                        ft.Text(company.location, color=TEXT_SECONDARY, size=12),
                        ft.Container(width=12),
                        ft.Icon(ft.Icons.PEOPLE_ROUNDED, color=TEXT_SECONDARY, size=14),
                        ft.Text(f"{emp_count} empleados", color=TEXT_SECONDARY, size=12),
                        ft.Container(width=12),
                        ft.Icon(ft.Icons.WORK_ROUNDED, color=TEXT_SECONDARY, size=14),
                        ft.Text(f"{total_jobs} vacantes", color=TEXT_SECONDARY, size=12),
                    ], spacing=4),
                ]),
                bgcolor=BG_CARD, border_radius=14,
                border=ft.border.all(1, BORDER_COLOR), padding=20,
                on_click=lambda e, c=company: show_company_projects(c),
                ink=True,
            )

        # ── Build grid ────────────────────────────────────────────────────────
        rows = []
        for i in range(0, len(companies), 2):
            row_items = [company_card(companies[i])]
            if i + 1 < len(companies):
                row_items.append(company_card(companies[i + 1]))
            else:
                row_items.append(ft.Container(expand=True))
            rows.append(ft.Row(
                controls=[ft.Container(content=c, expand=True) for c in row_items],
                spacing=12,
            ))

        grid = ft.Column(controls=rows, spacing=12) if rows else ft.Text(
            "No hay empresas registradas.", color=TEXT_SECONDARY
        )

        # ── Swap skeleton → real content ──────────────────────────────────────
        grid_container.content = grid
        try:
            grid_container.update()
        except Exception:
            pass

    threading.Thread(target=_load_data, daemon=True).start()
    return layout
