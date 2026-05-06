"""Projects view - Browse projects published by companies. Clicking 'Unirse' shows vacancies."""

import threading
import flet as ft
from utils.colors import (
    BG_CARD, BG_INPUT, BG_PRIMARY, TEXT_PRIMARY, TEXT_SECONDARY,
    ACCENT_PRIMARY, ACCENT_SUCCESS, ACCENT_WARNING, BORDER_COLOR,
)
from components.skill_tag import skill_tag
from services.graph_service import GraphService


def _skel(width=None, height=14, radius=8):
    return ft.Container(width=width, height=height, bgcolor="#1e2444", border_radius=radius)


def _skeleton_loader():
    """Skeleton list of project cards."""
    def card_skel():
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(controls=[
                        ft.Container(width=40, height=40, bgcolor="#1e2444", border_radius=10),
                        ft.Column(controls=[
                            _skel(width=180, height=16),
                            _skel(width=120, height=12),
                        ], spacing=6, expand=True),
                        _skel(width=70, height=22, radius=20),
                    ], spacing=12),
                    _skel(height=12),
                    _skel(width=250, height=12),
                    ft.Row(controls=[_skel(w, 12) for w in (60, 70, 55, 65)], spacing=4),
                    ft.Container(height=4),
                    ft.Row(controls=[
                        _skel(width=120, height=12),
                        ft.Container(expand=True),
                        _skel(width=130, height=30, radius=8),
                    ]),
                ],
                spacing=10,
            ),
            bgcolor=BG_CARD, border_radius=14,
            border=ft.border.all(1, BORDER_COLOR), padding=20,
        )

    return ft.Column(
        controls=[card_skel() for _ in range(4)],
        spacing=10,
    )


def projects_content(page: ft.Page, on_view_profile=None):
    """Build the projects view with vacancy dialogs — data loads in a background thread."""
    service = GraphService()

    # ── Header (rendered immediately) ─────────────────────────────────────────
    header = ft.Row(
        controls=[
            ft.Text("Proyectos", color=TEXT_PRIMARY, size=24, weight=ft.FontWeight.BOLD),
            ft.Container(expand=True),
            ft.TextField(
                hint_text="Buscar proyectos...", prefix_icon=ft.Icons.SEARCH_ROUNDED,
                border_color=BORDER_COLOR, focused_border_color=ACCENT_PRIMARY,
                bgcolor=BG_INPUT, color=TEXT_PRIMARY, hint_style=ft.TextStyle(color=TEXT_SECONDARY),
                cursor_color=ACCENT_PRIMARY, border_radius=12, height=42, text_size=13, width=280,
            ),
        ],
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    list_container = ft.Container(content=_skeleton_loader(), expand=True)

    layout = ft.Column(
        controls=[header, ft.Container(height=12), list_container],
        spacing=0, scroll=ft.ScrollMode.AUTO, expand=True,
    )

    # ── Background loader ─────────────────────────────────────────────────────
    import time
    def _load_data():
        time.sleep(0.05)
        try:
            current_user = service.get_current_user()
            admin_company = service.get_admin_company(current_user.id)

            if admin_company:
                projects_to_show = service.get_company_projects(admin_company.id)
                my_applications = []
            else:
                user_projects = service.get_user_projects(current_user.id)
                my_applications = service.get_user_applications(current_user.id)
                applied_projects_ids = [service.get_job(jid).project_id for jid in my_applications if service.get_job(jid)]
                visible_project_ids = set([p.id for p in user_projects] + applied_projects_ids)
                projects_to_show = [service.get_project(pid) for pid in visible_project_ids if service.get_project(pid)]

            # Pre-cache vacancies and match data for all projects
            project_vacancies_cache = {}
            match_cache = {}
            applied_cache = {}
            vacancy_applicants_cache = {}
            for proj in projects_to_show:
                vacancies = service.get_project_jobs(proj.id)
                project_vacancies_cache[proj.id] = vacancies
                for job in vacancies:
                    match_cache[job.id] = service.get_skill_match_percent(current_user.id, job.id)
                    applied_cache[job.id] = service.has_applied(current_user.id, job.id)
                    vacancy_applicants_cache[job.id] = service.get_job_applicants_count(job.id)
        except Exception:
            return

        status_colors = {"Active": ACCENT_SUCCESS, "Completed": ACCENT_PRIMARY, "On Hold": ACCENT_WARNING}
        status_map = {"Active": "Activo", "Completed": "Completado", "On Hold": "En pausa"}

        def show_vacancies(project):
            """Show vacancies dialog for a project."""
            vacancies = project_vacancies_cache.get(project.id, [])

            def apply_to_job(e, job_id):
                # Re-check occupancy before applying
                current_applicants = service.get_job_applicants_count(job_id)
                if current_applicants > 0:
                    occupied_dlg = ft.AlertDialog(
                        title=ft.Text("Vacante ocupada", color=TEXT_PRIMARY),
                        content=ft.Text("Esta vacante ya ha sido tomada por otro usuario.",
                                        color=TEXT_SECONDARY),
                        bgcolor=BG_CARD,
                        actions=[
                            ft.Container(
                                content=ft.Text("Entendido", color=TEXT_PRIMARY, size=13),
                                bgcolor=ACCENT_PRIMARY, border_radius=8,
                                padding=ft.padding.symmetric(horizontal=20, vertical=8),
                                on_click=lambda e: _close_dialog(occupied_dlg),
                                ink=True,
                            ),
                        ],
                    )
                    page.overlay.append(occupied_dlg)
                    occupied_dlg.open = True
                    page.update()
                    return

                service.apply_to_job(current_user.id, job_id)

                # Update button state immediately
                e.control.content.value = "Aplicado"
                e.control.content.color = ACCENT_SUCCESS
                e.control.bgcolor = ACCENT_SUCCESS + "20"
                e.control.on_click = None

                # Show success dialog
                success_dlg = ft.AlertDialog(
                    title=ft.Text("¡Aplicación exitosa!", color=TEXT_PRIMARY),
                    content=ft.Text("Tu aplicación ha sido enviada correctamente.",
                                    color=TEXT_SECONDARY),
                    bgcolor=BG_CARD,
                    actions=[
                        ft.Container(
                            content=ft.Text("Aceptar", color=TEXT_PRIMARY, size=13),
                            bgcolor=ACCENT_PRIMARY, border_radius=8,
                            padding=ft.padding.symmetric(horizontal=20, vertical=8),
                            on_click=lambda e: _close_dialog(success_dlg),
                            ink=True,
                        ),
                    ],
                )
                page.overlay.append(success_dlg)
                success_dlg.open = True
                page.update()

            def _close_dialog(dlg_to_close):
                dlg_to_close.open = False
                page.update()

            # Check if user is admin of this project's company
            is_own_company = admin_company and project.company_name == admin_company.name

            vacancy_items = []
            if vacancies:
                for job in vacancies:
                    match = match_cache.get(job.id, 0)
                    match_color = ACCENT_SUCCESS if match >= 60 else "#f59e0b" if match >= 30 else TEXT_SECONDARY
                    has_applied = applied_cache.get(job.id, False)
                    applicants = vacancy_applicants_cache.get(job.id, 0)
                    is_occupied = applicants > 0 and not has_applied

                    # Determine button state
                    if is_own_company:
                        btn_text = "Tu Vacante"
                        btn_color = ACCENT_SUCCESS
                        btn_bg = ACCENT_SUCCESS + "20"
                        btn_click = None
                    elif has_applied:
                        btn_text = "Aplicado"
                        btn_color = ACCENT_SUCCESS
                        btn_bg = ACCENT_SUCCESS + "20"
                        btn_click = None
                    elif is_occupied:
                        btn_text = "Ocupada"
                        btn_color = TEXT_SECONDARY
                        btn_bg = "#8b949e15"
                        btn_click = None
                    else:
                        btn_text = "Aplicar"
                        btn_color = TEXT_PRIMARY
                        btn_bg = ACCENT_PRIMARY
                        btn_click = lambda e, jid=job.id: apply_to_job(e, jid)

                    vacancy_items.append(ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Column(
                                    controls=[
                                        ft.Text(job.title, color=TEXT_PRIMARY, size=14, weight=ft.FontWeight.W_600),
                                        ft.Row(
                                            controls=[
                                                ft.Text(job.location, color=TEXT_SECONDARY, size=11),
                                                ft.Text("•", color=TEXT_SECONDARY),
                                                ft.Text(job.salary_range, color=ACCENT_SUCCESS, size=11),
                                            ],
                                            spacing=6,
                                        ),
                                        ft.Row(
                                            controls=[skill_tag(s) for s in job.required_skills[:4]],
                                            spacing=4,
                                        ),
                                    ],
                                    spacing=4, expand=True,
                                ),
                                ft.Column(
                                    controls=[
                                        ft.Text(f"{match}%", color=match_color, size=18,
                                                weight=ft.FontWeight.BOLD),
                                        ft.Text("Match", color=TEXT_SECONDARY, size=10),
                                        ft.Container(height=4),
                                        ft.Container(
                                            content=ft.Text(
                                                btn_text,
                                                color=btn_color,
                                                size=12, weight=ft.FontWeight.W_500,
                                            ),
                                            bgcolor=btn_bg,
                                            border_radius=8,
                                            padding=ft.padding.symmetric(horizontal=14, vertical=6),
                                            on_click=btn_click,
                                            ink=True,
                                        ),
                                    ],
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                ),
                            ],
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        bgcolor=BG_PRIMARY,
                        border_radius=10,
                        border=ft.border.all(1, BORDER_COLOR),
                        padding=12,
                    ))
            else:
                vacancy_items.append(ft.Text("No hay vacantes disponibles", color=TEXT_SECONDARY))

            dlg = ft.AlertDialog(
                title=ft.Text(f"Vacantes en: {project.name}", color=TEXT_PRIMARY, size=16,
                              weight=ft.FontWeight.W_600),
                content=ft.Container(
                    content=ft.Column(controls=vacancy_items, spacing=8, scroll=ft.ScrollMode.AUTO),
                    width=500, height=400,
                ),
                bgcolor=BG_CARD,
                actions=[
                    ft.Container(
                        content=ft.Text("Cerrar", color=TEXT_SECONDARY, size=13),
                        border=ft.border.all(1, BORDER_COLOR), border_radius=8,
                        padding=ft.padding.symmetric(horizontal=20, vertical=8),
                        on_click=lambda e: _close_dialog(dlg), ink=True,
                    ),
                ],
            )
            page.overlay.append(dlg)
            dlg.open = True
            page.update()

        def project_card(project):
            color = status_colors.get(project.status, TEXT_SECONDARY)
            vacancies = project_vacancies_cache.get(project.id, [])

            # Build applications section (only for regular users)
            applications_section = []
            if not admin_company and my_applications:
                applied_in_project = [
                    jid for jid in my_applications
                    if service.get_job(jid) and service.get_job(jid).project_id == project.id
                ]
                if applied_in_project:
                    applications_section = [
                        ft.Column(
                            controls=[
                                ft.Text("Tus aplicaciones:", color=TEXT_PRIMARY, size=12, weight=ft.FontWeight.W_600),
                                *[ft.Row(
                                    controls=[
                                        ft.Icon(ft.Icons.CHECK_CIRCLE_ROUNDED, color=ACCENT_SUCCESS, size=14),
                                        ft.Text(service.get_job(jid).title, color=TEXT_SECONDARY, size=12),
                                    ], spacing=6
                                ) for jid in applied_in_project]
                            ], spacing=4
                        ),
                        ft.Container(height=8),
                    ]

            # Admin sees "Ver Vacantes", regular user sees "Unirse / Vacantes"
            btn_label = "Ver Vacantes" if admin_company else "Unirse / Vacantes"

            return ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Container(
                                    content=ft.Icon(ft.Icons.FOLDER_ROUNDED, color=ACCENT_PRIMARY, size=20),
                                    bgcolor=ACCENT_PRIMARY + "20", border_radius=10, padding=10,
                                ),
                                ft.Column(
                                    controls=[
                                        ft.Text(project.name, color=TEXT_PRIMARY, size=15,
                                                weight=ft.FontWeight.W_600, max_lines=1,
                                                overflow=ft.TextOverflow.ELLIPSIS),
                                        ft.Text(f"por {project.company_name}", color=ACCENT_PRIMARY, size=12),
                                    ],
                                    spacing=2, expand=True,
                                ),
                                ft.Container(
                                    content=ft.Text(status_map.get(project.status, project.status),
                                                    color=color, size=11, weight=ft.FontWeight.W_500),
                                    bgcolor=color + "20", border_radius=20,
                                    padding=ft.padding.symmetric(horizontal=12, vertical=4),
                                ),
                            ],
                            spacing=12,
                        ),
                        ft.Text(project.description, color=TEXT_SECONDARY, size=13, max_lines=2,
                                overflow=ft.TextOverflow.ELLIPSIS),
                        ft.Container(height=4),
                        ft.Row(
                            controls=[skill_tag(t) for t in project.technologies[:5]],
                            wrap=True, spacing=4, run_spacing=4,
                        ),
                        ft.Container(height=8),
                        *applications_section,
                        ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.WORK_ROUNDED, color=TEXT_SECONDARY, size=14),
                                ft.Text(f"{len(vacancies)} vacantes", color=TEXT_SECONDARY, size=12),
                                ft.Container(expand=True),
                                ft.Container(
                                    content=ft.Text(btn_label, color=TEXT_PRIMARY, size=12,
                                                    weight=ft.FontWeight.W_500),
                                    bgcolor=ACCENT_PRIMARY, border_radius=8,
                                    padding=ft.padding.symmetric(horizontal=16, vertical=7),
                                    on_click=lambda e, p=project: show_vacancies(p),
                                    ink=True,
                                ),
                            ],
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                    ],
                ),
                bgcolor=BG_CARD, border_radius=14,
                border=ft.border.all(1, BORDER_COLOR), padding=20,
            )

        # ── Build project cards ────────────────────────────────────────────────
        cards = [project_card(p) for p in projects_to_show]
        if not cards:
            empty_msg = "No hay proyectos publicados por tu empresa." if admin_company else "No tienes proyectos asignados ni aplicaciones activas."
            cards = [ft.Text(empty_msg, color=TEXT_SECONDARY)]

        # ── Swap skeleton → real content ──────────────────────────────────────
        list_container.content = ft.Column(controls=cards, spacing=10)
        try:
            list_container.update()
            page.update()
        except Exception:
            pass

    page.run_thread(_load_data)
    return layout
