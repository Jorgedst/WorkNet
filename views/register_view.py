"""Register page view - User registration with skill selection and title dropdown."""

import flet as ft
import uuid
import random
from utils.colors import (
    BG_PRIMARY, BG_SECONDARY, BG_INPUT, BG_CARD, TEXT_PRIMARY, TEXT_SECONDARY,
    ACCENT_PRIMARY, ACCENT_DANGER, BORDER_COLOR, GRADIENT_START, GRADIENT_END,
)
from services.graph_service import GraphService, PREDEFINED_TITLES, PREDEFINED_SKILLS
from models.models import User
from components.skill_tag import skill_tag


def register_view(page: ft.Page):
    """Build registration page with title dropdown and skill chip selector."""
    service = GraphService()
    error_text = ft.Text("", color=ACCENT_DANGER, size=12, visible=False)
    selected_skills = []

    def _field(label, hint, icon, password=False):
        return ft.TextField(
            label=label, hint_text=hint, prefix_icon=icon,
            password=password, can_reveal_password=password,
            border_color=BORDER_COLOR, focused_border_color=ACCENT_PRIMARY,
            bgcolor=BG_INPUT, color=TEXT_PRIMARY,
            label_style=ft.TextStyle(color=TEXT_SECONDARY),
            hint_style=ft.TextStyle(color=TEXT_SECONDARY),
            cursor_color=ACCENT_PRIMARY, border_radius=12, height=52, text_size=14,
        )

    name_f = _field("Nombre completo", "Juan Pérez", ft.Icons.PERSON_ROUNDED)
    email_f = _field("Correo electrónico", "juan@worknet.com", ft.Icons.EMAIL_ROUNDED)
    pass_f = _field("Contraseña", "••••••••", ft.Icons.LOCK_ROUNDED, password=True)
    confirm_f = _field("Confirmar contraseña", "••••••••", ft.Icons.LOCK_ROUNDED, password=True)

    # Title dropdown
    title_dropdown = ft.Dropdown(
        label="Título profesional",
        options=[ft.dropdown.Option(t) for t in PREDEFINED_TITLES],
        border_color=BORDER_COLOR,
        focused_border_color=ACCENT_PRIMARY,
        bgcolor=BG_INPUT,
        color=TEXT_PRIMARY,
        label_style=ft.TextStyle(color=TEXT_SECONDARY),
        border_radius=12,
        height=55,
        text_size=14,
    )

    # Skills chip selector
    skills_container = ft.Ref[ft.Row]()

    def toggle_skill(skill_name):
        if skill_name in selected_skills:
            selected_skills.remove(skill_name)
        else:
            selected_skills.append(skill_name)
        _rebuild_skills()

    def _rebuild_skills():
        skills_container.current.controls = [_skill_chip(s) for s in PREDEFINED_SKILLS]
        skills_container.current.update()

    def _skill_chip(name):
        is_selected = name in selected_skills
        from utils.colors import get_skill_color
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

    def do_register(e):
        name = name_f.value.strip() if name_f.value else ""
        email = email_f.value.strip() if email_f.value else ""
        title = title_dropdown.value or ""
        password = pass_f.value.strip() if pass_f.value else ""
        confirm = confirm_f.value.strip() if confirm_f.value else ""

        if not all([name, email, title, password, confirm]):
            error_text.value = "Por favor, completa todos los campos."
            error_text.visible = True
            page.update()
            return
        if password != confirm:
            error_text.value = "Las contraseñas no coinciden."
            error_text.visible = True
            page.update()
            return
        if len(selected_skills) == 0:
            error_text.value = "Selecciona al menos una habilidad."
            error_text.visible = True
            page.update()
            return

        for u in service.users.values():
            if u.email == email:
                error_text.value = "Este correo ya está registrado."
                error_text.visible = True
                page.update()
                return

        avatar_colors = ["#2563eb", "#7c3aed", "#059669", "#dc2626", "#d97706", "#0891b2", "#e11d48"]
        new_user = User(
            id=f"u{uuid.uuid4().hex[:6]}", name=name, email=email,
            password=password, title=title, avatar_color=random.choice(avatar_colors),
            skills=list(selected_skills), is_online=True,
        )
        service.create_user(new_user)
        service.current_user_id = new_user.id
        page.go("/app/dashboard")

    register_card = ft.Container(
        content=ft.Column(
            controls=[
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Icon(ft.Icons.HUB_ROUNDED, color=TEXT_PRIMARY, size=24),
                                bgcolor=ACCENT_PRIMARY, border_radius=10, padding=8,
                            ),
                            ft.Text("WorkNet", color=TEXT_PRIMARY, size=24, weight=ft.FontWeight.BOLD),
                        ],
                        spacing=10, alignment=ft.MainAxisAlignment.CENTER,
                    ),
                ),
                ft.Text("Crear cuenta", color=TEXT_PRIMARY, size=20,
                        weight=ft.FontWeight.W_600, text_align=ft.TextAlign.CENTER),
                ft.Text("Únete a la red profesional", color=TEXT_SECONDARY, size=13,
                        text_align=ft.TextAlign.CENTER),
                ft.Container(height=12),
                name_f, email_f, title_dropdown, pass_f, confirm_f,
                ft.Container(height=8),
                ft.Text("Selecciona tus habilidades", color=TEXT_PRIMARY, size=14,
                        weight=ft.FontWeight.W_500),
                ft.Container(
                    content=ft.Row(
                        ref=skills_container,
                        controls=[_skill_chip(s) for s in PREDEFINED_SKILLS],
                        wrap=True, spacing=6, run_spacing=6,
                    ),
                    bgcolor=BG_CARD, border_radius=12,
                    border=ft.border.all(1, BORDER_COLOR),
                    padding=12, height=140,
                ),
                error_text,
                ft.Container(height=4),
                ft.Container(
                    content=ft.Container(
                        content=ft.Text("Crear Cuenta", color=TEXT_PRIMARY, size=15,
                                        weight=ft.FontWeight.W_600, text_align=ft.TextAlign.CENTER),
                        bgcolor=ACCENT_PRIMARY, border_radius=12,
                        padding=ft.padding.symmetric(vertical=14),
                        width=460, alignment=ft.Alignment(0, 0),
                        on_click=do_register, ink=True,
                    ),
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(height=8),
                ft.Row(
                    controls=[
                        ft.Text("¿Ya tienes cuenta?", color=TEXT_SECONDARY, size=13),
                        ft.Container(
                            content=ft.Text("Inicia sesión", color=ACCENT_PRIMARY, size=13,
                                            weight=ft.FontWeight.W_600),
                            on_click=lambda e: page.go("/"), ink=True,
                            padding=ft.padding.symmetric(horizontal=8, vertical=4), border_radius=6,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER, spacing=0,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=4, scroll=ft.ScrollMode.AUTO,
        ),
        width=500, bgcolor=BG_SECONDARY, border_radius=20,
        border=ft.border.all(1, BORDER_COLOR), padding=32,
        shadow=ft.BoxShadow(spread_radius=0, blur_radius=40, color="#00000060", offset=ft.Offset(0, 10)),
    )

    branding = ft.Container(
        content=ft.Column(
            controls=[
                ft.Container(expand=True),
                ft.Icon(ft.Icons.GROUP_ADD_ROUNDED, color="#30ffffff", size=100),
                ft.Container(height=20),
                ft.Text("Expande tu red", color=TEXT_PRIMARY, size=24,
                        weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                ft.Text("Únete a la comunidad de talento y\nencuentra tu próximo desafío",
                        color="#aaffffff", size=14, text_align=ft.TextAlign.CENTER),
                ft.Container(expand=True),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        expand=True,
        gradient=ft.LinearGradient(
            begin=ft.Alignment(1, -1), end=ft.Alignment(-1, 1),
            colors=[GRADIENT_END, GRADIENT_START],
        ),
        border_radius=ft.border_radius.only(top_left=20, bottom_left=20),
        padding=40,
    )

    return ft.View(
        route="/register",
        controls=[
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Container(content=register_card, alignment=ft.Alignment(0, 0), expand=True),
                        branding,
                    ],
                    spacing=0, expand=True,
                ),
                bgcolor=BG_PRIMARY, expand=True,
            ),
        ],
        bgcolor=BG_PRIMARY, padding=0, spacing=0,
    )
