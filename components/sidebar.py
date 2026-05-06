"""Sidebar navigation component matching the ProNetwork design."""

import flet as ft
from utils.colors import (
    BG_SECONDARY, SIDEBAR_ACTIVE_BG, SIDEBAR_HOVER_BG,
    TEXT_PRIMARY, TEXT_SECONDARY, ACCENT_SUCCESS, SIDEBAR_WIDTH, BORDER_COLOR,
)


def create_sidebar(page: ft.Page, active_route: str, on_navigate, current_user=None):
    """Build the sidebar with user info and navigation items."""

    nav_items = [
        {"icon": ft.Icons.DASHBOARD_ROUNDED,   "label": "Dashboard",  "route": "dashboard"},
        {"icon": ft.Icons.PEOPLE_ROUNDED,       "label": "Mi Red",     "route": "network"},
        {"icon": ft.Icons.FOLDER_ROUNDED,       "label": "Proyectos",  "route": "projects"},
        {"icon": ft.Icons.WORK_ROUNDED,         "label": "Vacantes",   "route": "jobs"},
        {"icon": ft.Icons.BUSINESS_ROUNDED,     "label": "Empresas",   "route": "companies"},
        {"icon": ft.Icons.ANALYTICS_ROUNDED,    "label": "Análisis",   "route": "graph"},
    ]

    def build_nav_item(item):
        is_active = active_route == item["route"]
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(item["icon"], color=TEXT_PRIMARY if is_active else TEXT_SECONDARY, size=20),
                    ft.Text(item["label"], color=TEXT_PRIMARY if is_active else TEXT_SECONDARY,
                            size=14, weight=ft.FontWeight.W_600 if is_active else ft.FontWeight.W_400),
                ],
                spacing=12,
            ),
            bgcolor=SIDEBAR_ACTIVE_BG if is_active else "transparent",
            border_radius=10,
            padding=ft.padding.symmetric(horizontal=16, vertical=12),
            on_click=lambda e, r=item["route"]: on_navigate(r),
            on_hover=lambda e: _on_hover(e, is_active),
            animate=ft.Animation(200, ft.AnimationCurve.EASE_IN_OUT),
        )

    def _on_hover(e, is_active):
        if not is_active:
            e.control.bgcolor = SIDEBAR_HOVER_BG if e.data == "true" else "transparent"
            e.control.update()

    # User profile section
    user_name = current_user.name if current_user else "Usuario"
    user_title = current_user.title if current_user else ""
    user_color = current_user.avatar_color if current_user else "#2563eb"
    user_initials = current_user.initials if current_user else "U"

    profile_section = ft.Container(
        content=ft.Row(
            controls=[
                ft.Container(
                    content=ft.CircleAvatar(
                        content=ft.Text(user_initials, size=14, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                        bgcolor=user_color,
                        radius=22,
                    ),
                    border=ft.border.all(2, ACCENT_SUCCESS),
                    border_radius=50,
                    padding=2,
                ),
                ft.Column(
                    controls=[
                        ft.Text(user_name, color=TEXT_PRIMARY, size=14, weight=ft.FontWeight.W_600,
                                max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                        ft.Text(user_title, color=TEXT_SECONDARY, size=11,
                                max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                    ],
                    spacing=2,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
            ],
            spacing=10,
        ),
        padding=ft.padding.symmetric(horizontal=16, vertical=20),
    )

    # Settings at bottom
    settings_item = ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(ft.Icons.SETTINGS_ROUNDED, color=TEXT_SECONDARY, size=20),
                ft.Text("Configuración", color=TEXT_SECONDARY, size=14),
                ft.Container(width=8, height=8, bgcolor=ACCENT_SUCCESS, border_radius=50),
            ],
            spacing=12,
        ),
        padding=ft.padding.symmetric(horizontal=16, vertical=12),
        border_radius=10,
        on_click=lambda e: on_navigate("settings"),
        on_hover=lambda e: _on_hover(e, active_route == "settings"),
    )

    return ft.Container(
        content=ft.Column(
            controls=[
                profile_section,
                ft.Divider(height=1, color=BORDER_COLOR),
                ft.Container(
                    content=ft.Column(
                        controls=[build_nav_item(item) for item in nav_items],
                        spacing=4,
                    ),
                    padding=ft.padding.symmetric(horizontal=10, vertical=10),
                    expand=True,
                ),
                ft.Divider(height=1, color=BORDER_COLOR),
                ft.Container(content=settings_item, padding=ft.padding.only(left=10, right=10, bottom=16)),
            ],
            spacing=0,
        ),
        width=SIDEBAR_WIDTH,
        bgcolor=BG_SECONDARY,
        border=ft.border.only(right=ft.BorderSide(1, BORDER_COLOR)),
    )
