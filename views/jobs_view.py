"""Vacantes view - Browse all job vacancies with apply dialog."""

import flet as ft
from utils.colors import (
    BG_CARD, BG_INPUT, BG_PRIMARY, TEXT_PRIMARY, TEXT_SECONDARY,
    ACCENT_PRIMARY, ACCENT_SUCCESS, BORDER_COLOR,
)
from components.skill_tag import skill_tag
from services.graph_service import GraphService


def jobs_content(page: ft.Page, on_view_profile=None):
    """Build the vacancies listing view with apply dialog."""
    service = GraphService()
    current_user = service.get_current_user()
    admin_company = service.get_admin_company(current_user.id)
    all_jobs = service.get_all_jobs()

    def apply_to_job(e, job_id, job_title):
        service.apply_to_job(current_user.id, job_id)
        
        # Update button state immediately
        e.control.content.value = "Aplicado"
        e.control.content.color = ACCENT_SUCCESS
        e.control.bgcolor = ACCENT_SUCCESS + "20"
        e.control.on_click = None
        

        dlg = ft.AlertDialog(
            title=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.CHECK_CIRCLE_ROUNDED, color=ACCENT_SUCCESS, size=28),
                    ft.Text("¡Aplicación exitosa!", color=TEXT_PRIMARY, size=16,
                            weight=ft.FontWeight.W_600),
                ],
                spacing=10,
            ),
            content=ft.Text(
                f"Has aplicado correctamente a la vacante:\n\"{job_title}\".\n\n"
                "La empresa revisará tu perfil y te contactará si eres seleccionado.",
                color=TEXT_SECONDARY, size=14,
            ),
            bgcolor=BG_CARD,
            actions=[
                ft.Container(
                    content=ft.Text("Entendido", color=TEXT_PRIMARY, size=13, weight=ft.FontWeight.W_500),
                    bgcolor=ACCENT_PRIMARY, border_radius=8,
                    padding=ft.padding.symmetric(horizontal=20, vertical=8),
                    on_click=lambda e: (setattr(dlg, "open", False), page.update()), ink=True,
                ),
            ],
        )
        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    def job_card(job):
        company = service.get_company(job.company_id)
        company_color = company.logo_color if company else ACCENT_PRIMARY
        company_initials = company.initials if company else "?"

        match = service.get_skill_match_percent(current_user.id, job.id)
        match_color = ACCENT_SUCCESS if match >= 60 else "#f59e0b" if match >= 30 else TEXT_SECONDARY
        has_applied = service.has_applied(current_user.id, job.id)

        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.CircleAvatar(
                        content=ft.Text(company_initials, size=16, weight=ft.FontWeight.BOLD,
                                        color=TEXT_PRIMARY),
                        bgcolor=company_color, radius=24,
                    ),
                    ft.Column(
                        controls=[
                            ft.Text(job.title, color=TEXT_PRIMARY, size=15, weight=ft.FontWeight.W_600),
                            ft.Row(
                                controls=[
                                    ft.Text(job.company_name, color=ACCENT_PRIMARY, size=13),
                                    ft.Text("•", color=TEXT_SECONDARY, size=13),
                                    ft.Text(job.project_name, color=TEXT_SECONDARY, size=12),
                                ],
                                spacing=6,
                            ),
                            ft.Row(
                                controls=[
                                    ft.Text(job.location, color=TEXT_SECONDARY, size=12),
                                ],
                                spacing=6,
                            ),
                            ft.Container(height=4),
                            ft.Row(
                                controls=[skill_tag(s) for s in job.required_skills[:5]],
                                wrap=True, spacing=4, run_spacing=4,
                            ),
                            ft.Container(height=4),
                            ft.Row(
                                controls=[
                                    ft.Container(
                                        content=ft.Text(job.job_type, color=TEXT_SECONDARY, size=11),
                                        bgcolor="#8b949e15", border_radius=6,
                                        padding=ft.padding.symmetric(horizontal=8, vertical=3),
                                    ),
                                    ft.Container(
                                        content=ft.Text(job.experience_level, color=TEXT_SECONDARY, size=11),
                                        bgcolor="#8b949e15", border_radius=6,
                                        padding=ft.padding.symmetric(horizontal=8, vertical=3),
                                    ),
                                    ft.Text(job.salary_range, color=ACCENT_SUCCESS, size=12,
                                            weight=ft.FontWeight.W_500),
                                ],
                                spacing=8,
                            ),
                        ],
                        spacing=2, expand=True,
                    ),
                    ft.Column(
                        controls=[
                            ft.Text(f"{match}%", color=match_color, size=20, weight=ft.FontWeight.BOLD),
                            ft.Text("Match", color=TEXT_SECONDARY, size=10),
                            ft.Container(height=8),
                            ft.Container(
                                content=ft.Text(
                                    "Tu Vacante" if admin_company else ("Aplicado" if has_applied else "Aplicar"),
                                    color=TEXT_PRIMARY if not has_applied and not admin_company else ACCENT_SUCCESS,
                                    size=12, weight=ft.FontWeight.W_500,
                                ),
                                bgcolor=ACCENT_PRIMARY if (not has_applied and not admin_company) else ACCENT_SUCCESS + "20",
                                border_radius=8,
                                padding=ft.padding.symmetric(horizontal=16, vertical=8),
                                on_click=(lambda e, jid=job.id, jt=job.title: apply_to_job(e, jid, jt))
                                if not has_applied and not admin_company else None,
                                ink=True,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                ],
                spacing=16,
                vertical_alignment=ft.CrossAxisAlignment.START,
            ),
            bgcolor=BG_CARD, border_radius=14,
            border=ft.border.all(1, BORDER_COLOR), padding=20,
        )

    header = ft.Row(
        controls=[
            ft.Text("Vacantes", color=TEXT_PRIMARY, size=24, weight=ft.FontWeight.BOLD),
            ft.Container(expand=True),
            ft.TextField(
                hint_text="Buscar vacantes...", prefix_icon=ft.Icons.SEARCH_ROUNDED,
                border_color=BORDER_COLOR, focused_border_color=ACCENT_PRIMARY,
                bgcolor=BG_INPUT, color=TEXT_PRIMARY, hint_style=ft.TextStyle(color=TEXT_SECONDARY),
                cursor_color=ACCENT_PRIMARY, border_radius=12, height=42, text_size=13, width=280,
            ),
        ],
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    if admin_company:
        list_items = []
        company_projects = service.get_company_projects(admin_company.id)
        for p in company_projects:
            list_items.append(ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.FOLDER_ROUNDED, color=ACCENT_PRIMARY, size=20),
                    ft.Text(f"Proyecto: {p.name}", color=TEXT_PRIMARY, size=18, weight=ft.FontWeight.W_600),
                ], spacing=10),
                margin=ft.margin.only(top=10, bottom=5)
            ))
            p_jobs = service.get_project_jobs(p.id)
            if p_jobs:
                list_items.extend([job_card(j) for j in p_jobs])
            else:
                list_items.append(ft.Text("No hay vacantes en este proyecto.", color=TEXT_SECONDARY, size=13))
            list_items.append(ft.Container(height=10))
    else:
        list_items = [job_card(j) for j in all_jobs]

    return ft.Column(
        controls=[header, ft.Container(height=12)] + list_items,
        spacing=10, scroll=ft.ScrollMode.AUTO, expand=True,
    )
