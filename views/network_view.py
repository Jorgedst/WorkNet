"""My Network view - Shows recommendations based on graph relationships."""

import flet as ft
from utils.colors import (
    BG_CARD, BG_INPUT, TEXT_PRIMARY, TEXT_SECONDARY,
    ACCENT_PRIMARY, ACCENT_SUCCESS, ACCENT_WARNING, BORDER_COLOR,
)
from components.skill_tag import skill_tag
from services.graph_service import GraphService


def _skel(width=None, height=14, radius=8):
    return ft.Container(width=width, height=height, bgcolor="#1e2444", border_radius=radius)

def _skeleton_loader():
    return ft.Column([
        ft.Row([_skel(width=150, height=80, radius=14), _skel(width=150, height=80, radius=14)], spacing=12),
        ft.Container(height=12),
        _skel(width=200, height=18),
        _skel(width=300, height=12),
        ft.Container(height=8),
        *[ft.Row([
            _skel(width=48, height=48, radius=24),
            ft.Column([_skel(width=120, height=14), _skel(width=80, height=10)], spacing=6)
        ], spacing=12) for _ in range(3)]
    ], spacing=10)

def network_content(page: ft.Page, on_view_profile=None):
    """Build the network view showing only graph-based recommendations."""
    import threading
    service = GraphService()

    _state = {"connections": [], "recommendations": [], "build_ui": None}

    def _on_search(e):
        query = (e.control.value or "").strip().lower()
        conn = _state["connections"]
        rec = _state["recommendations"]
        build = _state["build_ui"]
        if not build:
            return
        if query:
            conn = [u for u in conn if query in u.name.lower() or query in (u.title or "").lower()]
            rec = [r for r in rec if query in r[0].name.lower() or query in (r[0].title or "").lower()]
        content_container.content = build(conn, rec)
        if content_container.page:
            content_container.update()

    def _btn(text, bgcolor, color, on_click):
        return ft.Container(
            content=ft.Text(text, color=color, size=12, weight=ft.FontWeight.W_500),
            bgcolor=bgcolor, border_radius=8,
            padding=ft.padding.symmetric(horizontal=14, vertical=7),
            on_click=on_click, ink=True,
        )

    header = ft.Row(
        controls=[
            ft.Text("Mi Red", color=TEXT_PRIMARY, size=24, weight=ft.FontWeight.BOLD),
            ft.Container(expand=True),
            ft.TextField(
                hint_text="Buscar por nombre o puesto...", prefix_icon=ft.Icons.SEARCH_ROUNDED,
                border_color=BORDER_COLOR, focused_border_color=ACCENT_PRIMARY,
                bgcolor=BG_INPUT, color=TEXT_PRIMARY, hint_style=ft.TextStyle(color=TEXT_SECONDARY),
                cursor_color=ACCENT_PRIMARY, border_radius=12, height=42, text_size=13, width=300,
                on_change=_on_search,
            ),
        ],
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    content_container = ft.Container(content=_skeleton_loader(), expand=True)

    layout = ft.Column(
        controls=[header, ft.Container(height=8), content_container],
        spacing=8, scroll=ft.ScrollMode.AUTO, expand=True,
    )

    import time
    def _load_data():
        time.sleep(0.05)
        try:
            current_user = service.get_current_user()
            connections = service.get_connections(current_user.id)
            recommendations = service.get_recommendations(current_user.id)
            all_projects = service.get_all_projects()
        except Exception:
            return

        def build_ui(filtered_conn, filtered_rec):
            stats = ft.Row(
                controls=[
                    _stat_card(str(len(filtered_conn)), "Conexiones", ft.Icons.PEOPLE_ROUNDED, ACCENT_PRIMARY),
                    _stat_card(str(len(filtered_rec)), "Sugerencias", ft.Icons.PERSON_ADD_ROUNDED, ACCENT_SUCCESS),
                ], spacing=12,
            )

            sections = [stats, ft.Container(height=12)]
            sections.append(ft.Text("Personas que podrías conocer", color=TEXT_PRIMARY, size=18, weight=ft.FontWeight.W_600))
            sections.append(ft.Text("Basado en habilidades y proyectos en común", color=TEXT_SECONDARY, size=13))
            sections.append(ft.Container(height=8))

            if filtered_rec:
                for other, score, shared_skills, shared_projects in filtered_rec:
                    reasons = []
                    if shared_skills:
                        reasons.append(f"{len(shared_skills)} habilidades en común")
                    if shared_projects:
                        proj_names = [p.name for p in all_projects if p.id in shared_projects]
                        if proj_names:
                            reasons.append(f"Proyecto: {', '.join(proj_names)}")
                    reason_text = " • ".join(reasons) if reasons else "Conexión sugerida"

                    card = ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.CircleAvatar(
                                    content=ft.Text(other.initials, size=14, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                                    bgcolor=other.avatar_color, radius=24,
                                ),
                                ft.Column(
                                    controls=[
                                        ft.Text(other.name, color=TEXT_PRIMARY, size=14, weight=ft.FontWeight.W_600),
                                        ft.Text(other.title, color=TEXT_SECONDARY, size=12),
                                        ft.Container(height=2),
                                        ft.Text(reason_text, color=ACCENT_PRIMARY, size=11, italic=True),
                                        ft.Container(height=4),
                                        ft.Row(controls=[skill_tag(s) for s in shared_skills[:4]], spacing=4),
                                    ], spacing=2, expand=True,
                                ),
                                _btn("Ver Perfil", ACCENT_PRIMARY, TEXT_PRIMARY,
                                     lambda e, uid=other.id: on_view_profile(uid) if on_view_profile else None),
                            ], vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        bgcolor=BG_CARD, border_radius=12, border=ft.border.all(1, BORDER_COLOR),
                        padding=ft.padding.symmetric(horizontal=16, vertical=14),
                    )
                    sections.append(card)
            else:
                sections.append(ft.Container(
                    content=ft.Text("No hay sugerencias disponibles", color=TEXT_SECONDARY, size=14), padding=20,
                ))

            sections.append(ft.Container(height=16))
            sections.append(ft.Text("Mis Conexiones", color=TEXT_PRIMARY, size=18, weight=ft.FontWeight.W_600))
            sections.append(ft.Container(height=4))

            if filtered_conn:
                for u in filtered_conn:
                    sections.append(ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.CircleAvatar(
                                    content=ft.Text(u.initials, size=12, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                                    bgcolor=u.avatar_color, radius=20,
                                ),
                                ft.Column(
                                    controls=[
                                        ft.Text(u.name, color=TEXT_PRIMARY, size=14, weight=ft.FontWeight.W_500),
                                        ft.Text(u.title, color=TEXT_SECONDARY, size=12),
                                    ], spacing=2, expand=True,
                                ),
                                ft.Row(controls=[skill_tag(s) for s in u.skills[:3]], spacing=4),
                                _btn("Ver Perfil", ACCENT_PRIMARY, TEXT_PRIMARY,
                                     lambda e, uid=u.id: on_view_profile(uid) if on_view_profile else None),
                            ], vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        bgcolor=BG_CARD, border_radius=12, border=ft.border.all(1, BORDER_COLOR),
                        padding=ft.padding.symmetric(horizontal=16, vertical=12),
                    ))
            else:
                sections.append(ft.Text("Aún no tienes conexiones", color=TEXT_SECONDARY, size=14))
                
            return ft.Column(controls=sections, spacing=8, expand=True)

        _state["connections"] = connections
        _state["recommendations"] = recommendations
        _state["build_ui"] = build_ui

        content_container.content = build_ui(connections, recommendations)
        if content_container.page:
            content_container.update()
            page.update()

    page.run_thread(_load_data)
    return layout


def _stat_card(value, label, icon, color):
    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Container(
                    content=ft.Icon(icon, color=color, size=22),
                    bgcolor=color + "20", border_radius=10, padding=10,
                ),
                ft.Column(
                    controls=[
                        ft.Text(value, color=TEXT_PRIMARY, size=22, weight=ft.FontWeight.BOLD),
                        ft.Text(label, color=TEXT_SECONDARY, size=12),
                    ],
                    spacing=2,
                ),
            ],
            spacing=12,
        ),
        bgcolor=BG_CARD, border_radius=14, border=ft.border.all(1, BORDER_COLOR),
        padding=ft.padding.symmetric(horizontal=20, vertical=16), expand=True,
    )
