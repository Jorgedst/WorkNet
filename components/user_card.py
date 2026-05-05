"""User profile card component matching the ProNetwork design."""

import flet as ft
from utils.colors import (
    BG_CARD, BG_CARD_HOVER, TEXT_PRIMARY, TEXT_SECONDARY,
    ACCENT_PRIMARY, ACCENT_SUCCESS, BORDER_COLOR,
)
from components.skill_tag import skill_tag


def user_card(user, on_view_profile=None, on_connect=None, show_connect=True):
    """Create a user card with avatar, skills, and action buttons."""

    def _on_hover(e):
        e.control.bgcolor = BG_CARD_HOVER if e.data == "true" else BG_CARD
        e.control.update()

    # Online indicator
    avatar_stack = ft.Stack(
        controls=[
            ft.CircleAvatar(
                content=ft.Text(user.initials, size=18, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                bgcolor=user.avatar_color,
                radius=30,
            ),
            *(
                [ft.Container(
                    width=14, height=14, bgcolor=ACCENT_SUCCESS,
                    border_radius=50,
                    border=ft.border.all(2, BG_CARD),
                    left=46, top=46,
                )] if user.is_online else []
            ),
        ],
        width=64, height=64,
    )

    # Skill tags (show up to 6)
    skills_row = ft.Row(
        controls=[skill_tag(s) for s in user.skills[:6]],
        wrap=True,
        spacing=4,
        run_spacing=4,
    )

    # Action buttons
    actions = []
    actions.append(
        ft.Container(
            content=ft.Text("Ver Perfil", color=TEXT_PRIMARY, size=12, weight=ft.FontWeight.W_500),
            bgcolor=ACCENT_PRIMARY,
            border_radius=8,
            padding=ft.padding.symmetric(horizontal=16, vertical=8),
            on_click=lambda e: on_view_profile(user.id) if on_view_profile else None,
            ink=True,
        )
    )
    if show_connect and on_connect:
        actions.append(
            ft.Container(
                content=ft.Text("Conectar", color=TEXT_SECONDARY, size=12, weight=ft.FontWeight.W_500),
                border=ft.border.all(1, BORDER_COLOR),
                border_radius=8,
                padding=ft.padding.symmetric(horizontal=16, vertical=8),
                on_click=lambda e: on_connect(user.id),
                ink=True,
            )
        )

    # 3-dot menu
    menu_btn = ft.PopupMenuButton(
        icon=ft.Icons.MORE_VERT_ROUNDED,
        icon_color=TEXT_SECONDARY,
        icon_size=18,
        items=[
            ft.PopupMenuItem(content=ft.Text("Ver perfil"), on_click=lambda e: on_view_profile(user.id) if on_view_profile else None),
            ft.PopupMenuItem(content=ft.Text("Compartir perfil")),
        ],
    )

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[ft.Container(expand=True), menu_btn],
                    alignment=ft.MainAxisAlignment.END,
                ),
                ft.Container(
                    content=avatar_stack,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Text(user.name, color=TEXT_PRIMARY, size=15, weight=ft.FontWeight.W_600,
                        text_align=ft.TextAlign.CENTER),
                ft.Text(user.title, color=TEXT_SECONDARY, size=12,
                        text_align=ft.TextAlign.CENTER),
                ft.Container(height=4),
                ft.Container(content=skills_row, alignment=ft.Alignment(0, 0)),
                ft.Container(height=8),
                ft.Row(
                    controls=actions,
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=8,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=4,
        ),
        bgcolor=BG_CARD,
        border_radius=16,
        border=ft.border.all(1, BORDER_COLOR),
        padding=ft.padding.only(left=16, right=16, top=4, bottom=16),
        on_hover=_on_hover,
        animate=ft.Animation(200, ft.AnimationCurve.EASE_IN_OUT),
        expand=True,
    )
