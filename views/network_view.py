"""My Network view - Shows recommendations based on graph relationships."""

import flet as ft
from utils.colors import (
    BG_CARD, BG_INPUT, TEXT_PRIMARY, TEXT_SECONDARY,
    ACCENT_PRIMARY, ACCENT_SUCCESS, ACCENT_WARNING, BORDER_COLOR,
)
from components.skill_tag import skill_tag
from services.graph_service import GraphService


def network_content(page: ft.Page, on_view_profile=None):
    """Build the network view showing only graph-based recommendations."""
    service = GraphService()
    current_user = service.get_current_user()
    connections = service.get_connections(current_user.id)
    recommendations = service.get_recommendations(current_user.id)

    def _btn(text, bgcolor, color, on_click):
        return ft.Container(
            content=ft.Text(text, color=color, size=12, weight=ft.FontWeight.W_500),
            bgcolor=bgcolor, border_radius=8,
            padding=ft.padding.symmetric(horizontal=14, vertical=7),
            on_click=on_click, ink=True,
        )

    # Stats
    stats = ft.Row(
        controls=[
            _stat_card(str(len(connections)), "Conexiones", ft.Icons.PEOPLE_ROUNDED, ACCENT_PRIMARY),
            _stat_card(str(len(recommendations)), "Sugerencias", ft.Icons.PERSON_ADD_ROUNDED, ACCENT_SUCCESS),
        ],
        spacing=12,
    )

    # Recommendations based on graph
    sections = [stats, ft.Container(height=12)]
    sections.append(ft.Text("Personas que podrías conocer", color=TEXT_PRIMARY, size=18,
                            weight=ft.FontWeight.W_600))
    sections.append(ft.Text("Basado en habilidades y proyectos en común", color=TEXT_SECONDARY, size=13))
    sections.append(ft.Container(height=8))

    if recommendations:
        for other, score, shared_skills, shared_projects in recommendations:
            # Build reason text
            reasons = []
            if shared_skills:
                reasons.append(f"{len(shared_skills)} habilidades en común")
            if shared_projects:
                proj_names = []
                for pid in shared_projects:
                    p = service.get_project(pid)
                    if p:
                        proj_names.append(p.name)
                if proj_names:
                    reasons.append(f"Proyecto: {', '.join(proj_names)}")
            reason_text = " • ".join(reasons) if reasons else "Conexión sugerida"

            card = ft.Container(
                content=ft.Row(
                    controls=[
                        ft.CircleAvatar(
                            content=ft.Text(other.initials, size=14, weight=ft.FontWeight.BOLD,
                                            color=TEXT_PRIMARY),
                            bgcolor=other.avatar_color, radius=24,
                        ),
                        ft.Column(
                            controls=[
                                ft.Text(other.name, color=TEXT_PRIMARY, size=14, weight=ft.FontWeight.W_600),
                                ft.Text(other.title, color=TEXT_SECONDARY, size=12),
                                ft.Container(height=2),
                                ft.Text(reason_text, color=ACCENT_PRIMARY, size=11,
                                        italic=True),
                                ft.Container(height=4),
                                ft.Row(
                                    controls=[skill_tag(s) for s in shared_skills[:4]],
                                    spacing=4,
                                ),
                            ],
                            spacing=2, expand=True,
                        ),
                        _btn("Ver Perfil", ACCENT_PRIMARY, TEXT_PRIMARY,
                             lambda e, uid=other.id: on_view_profile(uid) if on_view_profile else None),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                bgcolor=BG_CARD, border_radius=12,
                border=ft.border.all(1, BORDER_COLOR),
                padding=ft.padding.symmetric(horizontal=16, vertical=14),
            )
            sections.append(card)
    else:
        sections.append(ft.Container(
            content=ft.Text("No hay sugerencias disponibles por ahora", color=TEXT_SECONDARY, size=14),
            padding=20,
        ))

    # Current connections
    sections.append(ft.Container(height=16))
    sections.append(ft.Text("Mis Conexiones", color=TEXT_PRIMARY, size=18, weight=ft.FontWeight.W_600))
    sections.append(ft.Container(height=4))
    if connections:
        for u in connections:
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
                            ],
                            spacing=2, expand=True,
                        ),
                        ft.Row(controls=[skill_tag(s) for s in u.skills[:3]], spacing=4),
                        _btn("Ver Perfil", ACCENT_PRIMARY, TEXT_PRIMARY,
                             lambda e, uid=u.id: on_view_profile(uid) if on_view_profile else None),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                bgcolor=BG_CARD, border_radius=12,
                border=ft.border.all(1, BORDER_COLOR),
                padding=ft.padding.symmetric(horizontal=16, vertical=12),
            ))
    else:
        sections.append(ft.Text("Aún no tienes conexiones", color=TEXT_SECONDARY, size=14))

    header = ft.Row(
        controls=[
            ft.Text("Mi Red", color=TEXT_PRIMARY, size=24, weight=ft.FontWeight.BOLD),
            ft.Container(expand=True),
            ft.TextField(
                hint_text="Buscar contactos...", prefix_icon=ft.Icons.SEARCH_ROUNDED,
                border_color=BORDER_COLOR, focused_border_color=ACCENT_PRIMARY,
                bgcolor=BG_INPUT, color=TEXT_PRIMARY, hint_style=ft.TextStyle(color=TEXT_SECONDARY),
                cursor_color=ACCENT_PRIMARY, border_radius=12, height=42, text_size=13, width=300,
            ),
        ],
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    return ft.Column(
        controls=[header] + sections,
        spacing=8, scroll=ft.ScrollMode.AUTO, expand=True,
    )


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
