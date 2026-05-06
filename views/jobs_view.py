"""Vacantes view - Browse all job vacancies with apply dialog."""

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
    """Skeleton list of job cards."""
    def job_skel():
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Container(width=48, height=48, bgcolor="#1e2444", border_radius=24),
                    ft.Column(
                        controls=[
                            _skel(width=220, height=16),
                            _skel(width=160, height=12),
                            ft.Row(controls=[_skel(w, 12) for w in (55, 65, 50)], spacing=6),
                        ],
                        spacing=8, expand=True,
                    ),
                    ft.Column(
                        controls=[_skel(width=50, height=22), _skel(width=70, height=28, radius=8)],
                        spacing=8, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                ],
                spacing=16,
                vertical_alignment=ft.CrossAxisAlignment.START,
            ),
            bgcolor=BG_CARD, border_radius=14,
            border=ft.border.all(1, BORDER_COLOR), padding=20,
        )

    return ft.Column(
        controls=[job_skel() for _ in range(6)],
        spacing=10,
    )


def jobs_content(page: ft.Page, on_view_profile=None):
    """Build the vacancies listing view — data loads in a background thread."""
    service = GraphService()

    # Shared mutable state
    _state = {"all_jobs": [], "companies_cache": {}, "card_builder": None}

    def _on_search(e):
        query = (e.control.value or "").strip().lower()
        jobs = _state["all_jobs"]
        build = _state["card_builder"]
        if build is None:
            return
        if query:
            jobs = [
                j for j in jobs
                if query in j.title.lower()
                or query in (j.company_name or "").lower()
                or query in (j.location or "").lower()
                or any(query in s.lower() for s in (j.required_skills or []))
            ]
        list_container.controls = [build(j, _state["companies_cache"].get(j.company_id)) for j in jobs] or [
            ft.Text("Sin resultados.", color=TEXT_SECONDARY)
        ]
        try:
            list_container.update()
        except Exception:
            pass

    # ── Header (rendered immediately) ─────────────────────────────────────────
    header = ft.Row(
        controls=[
            ft.Text("Vacantes", color=TEXT_PRIMARY, size=24, weight=ft.FontWeight.BOLD),
            ft.Container(expand=True),
            ft.TextField(
                hint_text="Buscar por título, empresa o habilidad...",
                prefix_icon=ft.Icons.SEARCH_ROUNDED,
                border_color=BORDER_COLOR, focused_border_color=ACCENT_PRIMARY,
                bgcolor=BG_INPUT, color=TEXT_PRIMARY, hint_style=ft.TextStyle(color=TEXT_SECONDARY),
                cursor_color=ACCENT_PRIMARY, border_radius=12, height=42, text_size=13, width=300,
                on_change=_on_search,
            ),
        ],
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    list_container = ft.Column(
        controls=[_skeleton_loader()],
        spacing=10, scroll=ft.ScrollMode.AUTO, expand=True,
    )

    layout = ft.Column(
        controls=[header, ft.Container(height=12), list_container],
        spacing=0, expand=True,
    )

    # ── Background loader ─────────────────────────────────────────────────────
    def _load_data():
        try:
            current_user  = service.get_current_user()
            admin_company = service.get_admin_company(current_user.id)
            all_jobs      = service.get_all_jobs()
        except Exception:
            return

        # ── Job card builder ──────────────────────────────────────────────────
        def apply_to_job(e, job_id, job_title):
            service.apply_to_job(current_user.id, job_id)
            e.control.content.value = "Aplicado"
            e.control.content.color = ACCENT_SUCCESS
            e.control.bgcolor = ACCENT_SUCCESS + "20"
            e.control.on_click = None

            dlg = ft.AlertDialog(
                title=ft.Row(controls=[
                    ft.Icon(ft.Icons.CHECK_CIRCLE_ROUNDED, color=ACCENT_SUCCESS, size=28),
                    ft.Text("¡Aplicación exitosa!", color=TEXT_PRIMARY, size=16,
                            weight=ft.FontWeight.W_600),
                ], spacing=10),
                content=ft.Text(
                    f"Has aplicado correctamente a la vacante:\n\"{job_title}\".\n\n"
                    "La empresa revisará tu perfil y te contactará si eres seleccionado.",
                    color=TEXT_SECONDARY, size=14,
                ),
                bgcolor=BG_CARD,
                actions=[ft.Container(
                    content=ft.Text("Entendido", color=TEXT_PRIMARY, size=13, weight=ft.FontWeight.W_500),
                    bgcolor=ACCENT_PRIMARY, border_radius=8,
                    padding=ft.padding.symmetric(horizontal=20, vertical=8),
                    on_click=lambda e: (setattr(dlg, "open", False), page.update()), ink=True,
                )],
            )
            page.overlay.append(dlg)
            dlg.open = True
            page.update()

        def job_card(job, company=None):
            company_color    = company.logo_color if company else ACCENT_PRIMARY
            company_initials = company.initials if company else "?"
            match      = service.get_skill_match_percent(current_user.id, job.id)
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
                                ft.Row(controls=[
                                    ft.Text(job.company_name, color=ACCENT_PRIMARY, size=13),
                                    ft.Text("•", color=TEXT_SECONDARY, size=13),
                                    ft.Text(job.project_name or "", color=TEXT_SECONDARY, size=12),
                                ], spacing=6),
                                ft.Row(controls=[
                                    ft.Text(job.location, color=TEXT_SECONDARY, size=12),
                                ], spacing=6),
                                ft.Container(height=4),
                                ft.Row(controls=[skill_tag(s) for s in job.required_skills[:5]],
                                       wrap=True, spacing=4, run_spacing=4),
                                ft.Container(height=4),
                                ft.Row(controls=[
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
                                ], spacing=8),
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

        # ── Build list items ──────────────────────────────────────────────────
        list_items = []
        if admin_company:
            company_projects = service.get_company_projects(admin_company.id)
            for p in company_projects:
                list_items.append(ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.FOLDER_ROUNDED, color=ACCENT_PRIMARY, size=20),
                        ft.Text(f"Proyecto: {p.name}", color=TEXT_PRIMARY, size=18,
                                weight=ft.FontWeight.W_600),
                    ], spacing=10),
                    margin=ft.margin.only(top=10, bottom=5),
                ))
                p_jobs = service.get_project_jobs(p.id)
                if p_jobs:
                    list_items.extend([job_card(j) for j in p_jobs])
                else:
                    list_items.append(ft.Text("No hay vacantes en este proyecto.",
                                               color=TEXT_SECONDARY, size=13))
                list_items.append(ft.Container(height=10))
        else:
            # Pre-fetch companies once to avoid N calls inside job_card
            companies_cache = {}
            for j in all_jobs:
                if j.company_id not in companies_cache:
                    companies_cache[j.company_id] = service.get_company(j.company_id)
            # Store in shared state for search filtering
            _state["all_jobs"]        = all_jobs
            _state["companies_cache"] = companies_cache
            _state["card_builder"]    = job_card
            list_items = [job_card(j, companies_cache.get(j.company_id)) for j in all_jobs]

        # ── Swap skeleton → real content ──────────────────────────────────────
        list_container.controls = list_items if list_items else [
            ft.Text("No hay vacantes disponibles.", color=TEXT_SECONDARY)
        ]
        try:
            list_container.update()
        except Exception:
            pass

    threading.Thread(target=_load_data, daemon=True).start()
    return layout
