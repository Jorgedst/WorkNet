"""Settings view - Profile editing, skill management, and logout."""

import flet as ft
from utils.colors import (
    BG_CARD, BG_INPUT, TEXT_PRIMARY, TEXT_SECONDARY,
    ACCENT_PRIMARY, ACCENT_DANGER, BORDER_COLOR,
)
from services.graph_service import GraphService, PREDEFINED_SKILLS
from utils.colors import get_skill_color


def settings_content(page: ft.Page, on_view_profile=None):
    """Build the settings view with profile edit, skill management, and logout."""
    service = GraphService()
    current_user = service.get_current_user()
    admin_company = service.get_admin_company(current_user.id)

    def _field(label, value, icon, enabled=True):
        return ft.TextField(
            label=label, value=value, prefix_icon=icon,
            border_color=BORDER_COLOR, focused_border_color=ACCENT_PRIMARY,
            bgcolor=BG_INPUT, color=TEXT_PRIMARY,
            label_style=ft.TextStyle(color=TEXT_SECONDARY),
            cursor_color=ACCENT_PRIMARY, border_radius=12, height=52, text_size=14,
            read_only=not enabled,
        )

    name_field = _field("Nombre", current_user.name, ft.Icons.PERSON_ROUNDED)
    email_field = _field("Correo", current_user.email, ft.Icons.EMAIL_ROUNDED, enabled=False)
    title_field = _field("Título", current_user.title, ft.Icons.WORK_ROUNDED, enabled=False)
    location_field = _field("Ubicación", current_user.location, ft.Icons.LOCATION_ON_ROUNDED)

    save_msg = ft.Text("", color="#22c55e", size=12, visible=False)

    def save_profile(e):
        current_user.name = name_field.value or current_user.name
        current_user.location = location_field.value or current_user.location
        # Recalculate initials
        parts = current_user.name.split()
        current_user.initials = "".join(p[0].upper() for p in parts[:2])
        service.update_user(current_user)
        save_msg.value = "✓ Cambios guardados"
        save_msg.visible = True
        page.update()

    # Skills management
    user_skills = list(current_user.skills)
    skills_container = ft.Ref[ft.Row]()

    def toggle_skill(skill_name):
        if skill_name in user_skills:
            user_skills.remove(skill_name)
        else:
            user_skills.append(skill_name)
        current_user.skills = list(user_skills)
        service.update_user(current_user)
        _rebuild_skills()

    def _rebuild_skills():
        skills_container.current.controls = [_skill_chip(s) for s in PREDEFINED_SKILLS]
        skills_container.current.update()

    def _skill_chip(name):
        is_selected = name in user_skills
        colors = get_skill_color(name)
        return ft.Container(
            content=ft.Text(name, color=TEXT_PRIMARY if is_selected else colors["text"],
                            size=11, weight=ft.FontWeight.W_500),
            bgcolor=ACCENT_PRIMARY if is_selected else colors["bg"],
            border=ft.border.all(1, ACCENT_PRIMARY if is_selected else colors["border"]),
            border_radius=8,
            padding=ft.padding.symmetric(horizontal=10, vertical=5),
            on_click=lambda e, s=name: toggle_skill(s),
            animate=ft.Animation(150, ft.AnimationCurve.EASE_IN_OUT),
        )

    # Profile section
    profile_section = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Información Personal", color=TEXT_PRIMARY, size=16, weight=ft.FontWeight.W_600),
                ft.Container(height=8),
                name_field, ft.Container(height=4),
                email_field, ft.Container(height=4),
                title_field, ft.Container(height=4),
                location_field,
                ft.Container(height=8),
                save_msg,
                ft.Container(
                    content=ft.Text("Guardar Cambios", color=TEXT_PRIMARY, size=13, weight=ft.FontWeight.W_600),
                    bgcolor=ACCENT_PRIMARY, border_radius=10,
                    padding=ft.padding.symmetric(horizontal=20, vertical=10),
                    on_click=save_profile, ink=True,
                ),
            ],
        ),
        bgcolor=BG_CARD, border_radius=14,
        border=ft.border.all(1, BORDER_COLOR), padding=20,
    )

    # Skills section
    if admin_company:
        skills_section = ft.Container()
    else:
        skills_section = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Mis Habilidades", color=TEXT_PRIMARY, size=16, weight=ft.FontWeight.W_600),
                    ft.Text("Haz clic para añadir o quitar habilidades", color=TEXT_SECONDARY, size=12),
                    ft.Container(height=8),
                    ft.Container(
                        content=ft.Row(
                            ref=skills_container,
                            controls=[_skill_chip(s) for s in PREDEFINED_SKILLS],
                            wrap=True, spacing=6, run_spacing=6,
                        ),
                        height=200,
                    ),
                ],
            ),
            bgcolor=BG_CARD, border_radius=14,
            border=ft.border.all(1, BORDER_COLOR), padding=20,
        )

    # Danger zone
    def _logout():
        service.current_user_id = None
        page.go("/")

    danger_section = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Zona de Peligro", color=TEXT_PRIMARY, size=16, weight=ft.FontWeight.W_600),
                ft.Container(height=8),
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Column(
                                controls=[
                                    ft.Text("Cerrar Sesión", color=TEXT_PRIMARY, size=14,
                                            weight=ft.FontWeight.W_500),
                                    ft.Text("Salir de tu cuenta", color=TEXT_SECONDARY, size=12),
                                ],
                                spacing=2, expand=True,
                            ),
                            ft.Container(
                                content=ft.Text("Cerrar Sesión", color=ACCENT_DANGER, size=12,
                                                weight=ft.FontWeight.W_600),
                                border=ft.border.all(1, ACCENT_DANGER), border_radius=8,
                                padding=ft.padding.symmetric(horizontal=14, vertical=8),
                                on_click=lambda e: _logout(), ink=True,
                            ),
                        ],
                    ),
                ),
            ],
        ),
        bgcolor=BG_CARD, border_radius=14,
        border=ft.border.all(1, BORDER_COLOR), padding=20,
    )

    header = ft.Text("Configuración", color=TEXT_PRIMARY, size=24, weight=ft.FontWeight.BOLD)

    return ft.Column(
        controls=[
            header,
            ft.Container(height=8),
            ft.Row(
                controls=[
                    ft.Container(
                        content=ft.Column(controls=[profile_section], spacing=12),
                        expand=3,
                    ),
                    ft.Container(
                        content=ft.Column(controls=[skills_section, danger_section], spacing=12),
                        expand=2,
                    ),
                ],
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.START,
            ),
        ],
        spacing=0, scroll=ft.ScrollMode.AUTO, expand=True,
    )
