"""Profile view - View and edit user profile."""

import flet as ft
from utils.colors import (
    BG_CARD, TEXT_PRIMARY, TEXT_SECONDARY, ACCENT_PRIMARY, ACCENT_SUCCESS,
    BORDER_COLOR, BG_INPUT,
)
from components.skill_tag import skill_tag
from services.graph_service import GraphService


def _skel(width=None, height=14, radius=8):
    return ft.Container(width=width, height=height, bgcolor="#1e2444", border_radius=radius)

def _skeleton_loader():
    return ft.Column([
        ft.Container(
            content=ft.Row([
                _skel(width=90, height=90, radius=45),
                ft.Column([_skel(width=200, height=22), _skel(width=150, height=14), _skel(width=250, height=14)], spacing=8, expand=True),
                _skel(width=60, height=40), _skel(width=60, height=40)
            ]), bgcolor=BG_CARD, border_radius=16, border=ft.border.all(1, BORDER_COLOR), padding=24
        ),
        ft.Row([
            ft.Container(content=_skel(height=150), expand=True, bgcolor=BG_CARD, border_radius=14, border=ft.border.all(1, BORDER_COLOR), padding=20),
            ft.Container(content=_skel(height=150), expand=True, bgcolor=BG_CARD, border_radius=14, border=ft.border.all(1, BORDER_COLOR), padding=20),
        ], spacing=12),
        ft.Container(content=_skel(height=200), bgcolor=BG_CARD, border_radius=14, border=ft.border.all(1, BORDER_COLOR), padding=20)
    ], spacing=12, expand=True)

def profile_content(page: ft.Page, user_id: str = None, on_view_profile=None):
    """Build the profile detail view."""
    import threading
    service = GraphService()
    current_user = service.get_current_user()

    if user_id and user_id != current_user.id:
        user = service.get_user(user_id)
        is_own = False
    else:
        user = current_user
        is_own = True

    if not user:
        return ft.Text("Usuario no encontrado", color=TEXT_SECONDARY, size=16)

    back_btn = ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(ft.Icons.ARROW_BACK_ROUNDED, color=TEXT_SECONDARY, size=18),
                ft.Text("Volver", color=TEXT_SECONDARY, size=13),
            ], spacing=6,
        ),
        on_click=lambda e: page.run_task(page.push_route, "/app/dashboard"),
        ink=True, border_radius=8, padding=ft.padding.symmetric(horizontal=10, vertical=6),
    ) if not is_own else ft.Container()

    content_container = ft.Container(content=_skeleton_loader(), expand=True)

    layout = ft.Column(
        controls=[back_btn, content_container],
        spacing=12, scroll=ft.ScrollMode.AUTO, expand=True,
    )

    def _load_data():
        try:
            company = service.get_user_company(user.id)
            connections = service.get_connections(user.id)
            projects = service.get_user_projects(user.id)
            similar = service.get_users_with_similar_skills(user.id)
            is_connected = service.is_connected(current_user.id, user.id) if not is_own else False
        except Exception:
            return

        def handle_connect(e):
            if not is_connected:
                service.send_connection_request(current_user.id, user.id)
                success_dlg = ft.AlertDialog(
                    title=ft.Text("Conexión solicitada", color=TEXT_PRIMARY),
                    content=ft.Text(f"Has enviado una solicitud a {user.name}.", color=TEXT_SECONDARY),
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
                e.control.content.value = "Pendiente"
                e.control.bgcolor = ACCENT_SUCCESS + "20"
                page.update()

        header_card = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Container(
                        content=ft.CircleAvatar(
                            content=ft.Text(user.initials, size=28, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                            bgcolor=user.avatar_color, radius=44,
                        ),
                        border=ft.border.all(3, ACCENT_PRIMARY if is_own else user.avatar_color),
                        border_radius=100, padding=3,
                    ),
                    ft.Container(width=8),
                    ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Text(user.name, color=TEXT_PRIMARY, size=22, weight=ft.FontWeight.BOLD),
                                    *([ft.Container(width=8, height=8, bgcolor=ACCENT_SUCCESS, border_radius=50)] if user.is_online else []),
                                ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            ft.Text(user.title, color=ACCENT_PRIMARY, size=14),
                            ft.Row(
                                controls=[
                                    ft.Icon(ft.Icons.LOCATION_ON_ROUNDED, color=TEXT_SECONDARY, size=14),
                                    ft.Text(user.location or "Sin ubicación", color=TEXT_SECONDARY, size=13),
                                    ft.Container(width=16),
                                    ft.Icon(ft.Icons.BUSINESS_ROUNDED, color=TEXT_SECONDARY, size=14),
                                    ft.Text(company.name if company else "Sin empresa", color=TEXT_SECONDARY, size=13),
                                ], spacing=4,
                            ),
                        ], spacing=4, expand=True,
                    ),
                    ft.Column(
                        controls=[
                            ft.Text(str(len(connections)), color=TEXT_PRIMARY, size=22, weight=ft.FontWeight.BOLD),
                            ft.Text("Conexiones", color=TEXT_SECONDARY, size=12),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Container(width=20),
                    ft.Column(
                        controls=[
                            ft.Text(str(len(projects)), color=TEXT_PRIMARY, size=22, weight=ft.FontWeight.BOLD),
                            ft.Text("Proyectos", color=TEXT_SECONDARY, size=12),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Container(width=20),
                    *([] if is_own else [
                        ft.Container(
                            content=ft.Text("Conectado" if is_connected else "Conectar", color=TEXT_PRIMARY, size=13, weight=ft.FontWeight.W_600),
                            bgcolor=ACCENT_SUCCESS if is_connected else ACCENT_PRIMARY,
                            border_radius=10, padding=ft.padding.symmetric(horizontal=20, vertical=10),
                            ink=True, on_click=handle_connect if not is_connected else None,
                        ),
                    ]),
                ], vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=BG_CARD, border_radius=16, border=ft.border.all(1, BORDER_COLOR), padding=24,
        )

        skills_section = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Habilidades", color=TEXT_PRIMARY, size=16, weight=ft.FontWeight.W_600),
                    ft.Container(height=8),
                    ft.Row(controls=[skill_tag(s, size="medium") for s in user.skills], wrap=True, spacing=6, run_spacing=6),
                ],
            ),
            bgcolor=BG_CARD, border_radius=14, border=ft.border.all(1, BORDER_COLOR), padding=20,
        )

        proj_items = []
        for p in projects:
            status_colors = {"Active": ACCENT_SUCCESS, "Completed": ACCENT_PRIMARY, "On Hold": "#f59e0b"}
            status_map = {"Active": "Activo", "Completed": "Completado", "On Hold": "En pausa"}
            proj_items.append(ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.FOLDER_ROUNDED, color=ACCENT_PRIMARY, size=18),
                        ft.Text(p.name, color=TEXT_PRIMARY, size=14, weight=ft.FontWeight.W_500, expand=True),
                        ft.Container(
                            content=ft.Text(status_map.get(p.status, p.status), color=status_colors.get(p.status, TEXT_SECONDARY), size=11),
                            bgcolor=status_colors.get(p.status, TEXT_SECONDARY) + "20",
                            border_radius=20, padding=ft.padding.symmetric(horizontal=10, vertical=3),
                        ),
                    ],
                ), padding=ft.padding.symmetric(vertical=6),
            ))

        projects_section = ft.Container(
            content=ft.Column(
                controls=[ft.Text("Proyectos", color=TEXT_PRIMARY, size=16, weight=ft.FontWeight.W_600)] + 
                         (proj_items if proj_items else [ft.Text("Sin proyectos", color=TEXT_SECONDARY, size=13)]),
            ),
            bgcolor=BG_CARD, border_radius=14, border=ft.border.all(1, BORDER_COLOR), padding=20,
        )

        sim_items = []
        for other_user, count, shared in similar[:5]:
            sim_items.append(ft.Container(
                content=ft.Row(
                    controls=[
                        ft.CircleAvatar(
                            content=ft.Text(other_user.initials, size=11, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                            bgcolor=other_user.avatar_color, radius=16,
                        ),
                        ft.Column(
                            controls=[
                                ft.Text(other_user.name, color=TEXT_PRIMARY, size=13, weight=ft.FontWeight.W_500),
                                ft.Text(f"{count} habilidades en común", color=TEXT_SECONDARY, size=11),
                            ], spacing=1, expand=True,
                        ),
                        ft.Container(
                            content=ft.Text("Ver", color=ACCENT_PRIMARY, size=11),
                            on_click=lambda e, uid=other_user.id: on_view_profile(uid) if on_view_profile else None,
                            ink=True, padding=ft.padding.symmetric(horizontal=10, vertical=4), border_radius=6,
                        ),
                    ],
                ), padding=ft.padding.symmetric(vertical=4),
            ))

        similar_section = ft.Container(
            content=ft.Column(
                controls=[ft.Text("Habilidades Similares", color=TEXT_PRIMARY, size=16, weight=ft.FontWeight.W_600)] + sim_items,
            ),
            bgcolor=BG_CARD, border_radius=14, border=ft.border.all(1, BORDER_COLOR), padding=20,
        )

        content_container.content = ft.Column(
            controls=[
                header_card,
                ft.Row(
                    controls=[
                        ft.Container(content=skills_section, expand=True),
                        ft.Container(content=similar_section, expand=True),
                    ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.START,
                ),
                projects_section,
            ], spacing=12,
        )
        if content_container.page:
            content_container.update()

    threading.Thread(target=_load_data, daemon=True).start()
    return layout
