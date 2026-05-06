"""Projects view - Browse projects published by companies. Clicking 'Unirse' shows vacancies."""

import flet as ft
from utils.colors import (
    BG_CARD, BG_INPUT, BG_PRIMARY, TEXT_PRIMARY, TEXT_SECONDARY,
    ACCENT_PRIMARY, ACCENT_SUCCESS, ACCENT_WARNING, BORDER_COLOR,
)
from components.skill_tag import skill_tag
from services.graph_service import GraphService


def projects_content(page: ft.Page, on_view_profile=None):
    """Build the projects view with vacancy dialogs."""
    service = GraphService()
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

    status_colors = {"Active": ACCENT_SUCCESS, "Completed": ACCENT_PRIMARY, "On Hold": ACCENT_WARNING}
    status_map = {"Active": "Activo", "Completed": "Completado", "On Hold": "En pausa"}

    def show_vacancies(project):
        """Show vacancies dialog for a project."""
        vacancies = service.get_project_jobs(project.id)

        def apply_to_job(e, job_id):
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

        vacancy_items = []
        if vacancies:
            for job in vacancies:
                match = service.get_skill_match_percent(current_user.id, job.id)
                match_color = ACCENT_SUCCESS if match >= 60 else "#f59e0b" if match >= 30 else TEXT_SECONDARY
                has_applied = service.has_applied(current_user.id, job.id)

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
                                            "Aplicado" if has_applied else "Aplicar",
                                            color=TEXT_PRIMARY if not has_applied else ACCENT_SUCCESS,
                                            size=12, weight=ft.FontWeight.W_500,
                                        ),
                                        bgcolor=ACCENT_PRIMARY if not has_applied else ACCENT_SUCCESS + "20",
                                        border_radius=8,
                                        padding=ft.padding.symmetric(horizontal=14, vertical=6),
                                        on_click=(lambda e, jid=job.id: apply_to_job(e, jid))
                                        if not has_applied else None,
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
        vacancies = service.get_project_jobs(project.id)

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
                    *(
                        [ft.Column(
                            controls=[
                                ft.Text("Tus aplicaciones:", color=TEXT_PRIMARY, size=12, weight=ft.FontWeight.W_600),
                                *[ft.Row(
                                    controls=[
                                        ft.Icon(ft.Icons.CHECK_CIRCLE_ROUNDED, color=ACCENT_SUCCESS, size=14),
                                        ft.Text(service.get_job(jid).title, color=TEXT_SECONDARY, size=12),
                                    ], spacing=6
                                ) for jid in my_applications if service.get_job(jid) and service.get_job(jid).project_id == project.id]
                            ], spacing=4
                        ), ft.Container(height=8)]
                        if any(service.get_job(jid) and service.get_job(jid).project_id == project.id for jid in my_applications) else []
                    ),
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.WORK_ROUNDED, color=TEXT_SECONDARY, size=14),
                            ft.Text(f"{len(vacancies)} vacantes disponibles", color=TEXT_SECONDARY, size=12),
                            ft.Container(expand=True),
                            ft.Container(
                                content=ft.Text("Unirse / Vacantes", color=TEXT_PRIMARY, size=12,
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

    return ft.Column(
        controls=[header, ft.Container(height=12)] + [project_card(p) for p in projects_to_show] +
                 ([ft.Text("No tienes proyectos asignados ni aplicaciones activas.", color=TEXT_SECONDARY)] if not projects_to_show else []),
        spacing=10, scroll=ft.ScrollMode.AUTO, expand=True,
    )
