"""Login page view - First page of the application."""

import flet as ft
from utils.colors import (
    BG_PRIMARY, BG_SECONDARY, BG_INPUT, TEXT_PRIMARY, TEXT_SECONDARY,
    ACCENT_PRIMARY, ACCENT_HOVER, ACCENT_DANGER, BORDER_COLOR, GRADIENT_START, GRADIENT_END,
)
from services.graph_service import GraphService


def login_view(page: ft.Page):
    """Build the login page with a modern dark theme split layout."""
    service = GraphService()
    error_text = ft.Text("", color=ACCENT_DANGER, size=12, visible=False)

    email_field = ft.TextField(
        label="Correo electrónico",
        hint_text="usuario@worknet.com",
        prefix_icon=ft.Icons.EMAIL_ROUNDED,
        border_color=BORDER_COLOR,
        focused_border_color=ACCENT_PRIMARY,
        bgcolor=BG_INPUT,
        color=TEXT_PRIMARY,
        label_style=ft.TextStyle(color=TEXT_SECONDARY),
        hint_style=ft.TextStyle(color=TEXT_SECONDARY),
        cursor_color=ACCENT_PRIMARY,
        border_radius=12,
        height=55,
        text_size=14,
    )

    password_field = ft.TextField(
        label="Contraseña",
        hint_text="••••••••",
        prefix_icon=ft.Icons.LOCK_ROUNDED,
        password=True,
        can_reveal_password=True,
        border_color=BORDER_COLOR,
        focused_border_color=ACCENT_PRIMARY,
        bgcolor=BG_INPUT,
        color=TEXT_PRIMARY,
        label_style=ft.TextStyle(color=TEXT_SECONDARY),
        hint_style=ft.TextStyle(color=TEXT_SECONDARY),
        cursor_color=ACCENT_PRIMARY,
        border_radius=12,
        height=55,
        text_size=14,
    )

    def do_login(e):
        email = email_field.value.strip() if email_field.value else ""
        password = password_field.value.strip() if password_field.value else ""

        if not email or not password:
            error_text.value = "Por favor, completa todos los campos."
            error_text.visible = True
            error_text.update()
            return

        user = service.authenticate(email, password)
        if user:
            service.current_user_id = user.id
            page.go("/app/dashboard")
        else:
            error_text.value = "Correo o contraseña incorrectos."
            error_text.visible = True
            error_text.update()

    def go_register(e):
        page.go("/register")

    # Login form card
    login_card = ft.Container(
        content=ft.Column(
            controls=[
                # Logo and title
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Icon(ft.Icons.HUB_ROUNDED, color=TEXT_PRIMARY, size=28),
                                bgcolor=ACCENT_PRIMARY,
                                border_radius=12,
                                padding=10,
                            ),
                            ft.Text("WorkNet", color=TEXT_PRIMARY, size=28, weight=ft.FontWeight.BOLD),
                        ],
                        spacing=12,
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                ),
                ft.Container(height=8),
                ft.Text("Bienvenido de vuelta", color=TEXT_PRIMARY, size=22,
                        weight=ft.FontWeight.W_600, text_align=ft.TextAlign.CENTER),
                ft.Text("Inicia sesión para acceder a tu red profesional",
                        color=TEXT_SECONDARY, size=13, text_align=ft.TextAlign.CENTER),
                ft.Container(height=24),
                email_field,
                ft.Container(height=4),
                password_field,
                ft.Container(height=4),
                error_text,
                ft.Container(height=8),
                ft.Container(
                    content=ft.Container(
                        content=ft.Text("Iniciar Sesión", color=TEXT_PRIMARY, size=15,
                                        weight=ft.FontWeight.W_600, text_align=ft.TextAlign.CENTER),
                        bgcolor=ACCENT_PRIMARY,
                        border_radius=12,
                        padding=ft.padding.symmetric(vertical=14),
                        width=400,
                        alignment=ft.Alignment(0, 0),
                        on_click=do_login,
                        ink=True,
                        animate=ft.Animation(200, ft.AnimationCurve.EASE_IN_OUT),
                    ),
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Container(height=16),
                ft.Row(
                    controls=[
                        ft.Container(content=ft.Divider(color=BORDER_COLOR), expand=True),
                        ft.Text("  o  ", color=TEXT_SECONDARY, size=12),
                        ft.Container(content=ft.Divider(color=BORDER_COLOR), expand=True),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Container(height=16),
                ft.Row(
                    controls=[
                        ft.Text("¿No tienes una cuenta?", color=TEXT_SECONDARY, size=13),
                        ft.Container(
                            content=ft.Text("Regístrate", color=ACCENT_PRIMARY, size=13,
                                            weight=ft.FontWeight.W_600),
                            on_click=go_register,
                            ink=True,
                            padding=ft.padding.symmetric(horizontal=8, vertical=4),
                            border_radius=6,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=0,
                ),
                ft.Row(
                    controls=[
                        ft.Text("¿Eres una empresa?", color=TEXT_SECONDARY, size=13),
                        ft.Container(
                            content=ft.Text("Publicar Vacantes", color=ACCENT_HOVER, size=13,
                                            weight=ft.FontWeight.W_600),
                            on_click=lambda e: page.go("/register-company"),
                            ink=True,
                            padding=ft.padding.symmetric(horizontal=8, vertical=4),
                            border_radius=6,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=0,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=4,
        ),
        width=440,
        bgcolor=BG_SECONDARY,
        border_radius=20,
        border=ft.border.all(1, BORDER_COLOR),
        padding=40,
        shadow=ft.BoxShadow(
            spread_radius=0, blur_radius=40,
            color="#00000060", offset=ft.Offset(0, 10),
        ),
    )

    # Right branding panel
    branding_panel = ft.Container(
        content=ft.Column(
            controls=[
                ft.Container(expand=True),
                ft.Icon(ft.Icons.HUB_ROUNDED, color="#30ffffff", size=120),
                ft.Container(height=20),
                ft.Text("Conecta. Colabora. Crece.", color=TEXT_PRIMARY,
                        size=26, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                ft.Container(height=10),
                ft.Text(
                    "Tu red profesional potenciada por\ntecnología de grafos",
                    color="#aaffffff", size=14, text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=30),
                # Feature highlights
                _feature_pill(ft.Icons.PEOPLE_ROUNDED, "Conexiones inteligentes"),
                _feature_pill(ft.Icons.TRENDING_UP_ROUNDED, "Recomendaciones basadas en grafos"),
                _feature_pill(ft.Icons.WORK_ROUNDED, "Oportunidades laborales"),
                ft.Container(expand=True),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8,
        ),
        expand=True,
        gradient=ft.LinearGradient(
            begin=ft.Alignment(-1, -1),
            end=ft.Alignment(1, 1),
            colors=[GRADIENT_START, GRADIENT_END],
        ),
        border_radius=ft.border_radius.only(top_right=0, bottom_right=0, top_left=20, bottom_left=20),
        padding=40,
    )

    return ft.View(
        route="/",
        controls=[
            ft.Container(
                content=ft.Row(
                    controls=[
                        # Left: Login form
                        ft.Container(
                            content=login_card,
                            alignment=ft.Alignment(0, 0),
                            expand=True,
                        ),
                        # Right: Branding
                        branding_panel,
                    ],
                    spacing=0,
                    expand=True,
                ),
                bgcolor=BG_PRIMARY,
                expand=True,
            ),
        ],
        bgcolor=BG_PRIMARY,
        padding=0,
        spacing=0,
    )


def _feature_pill(icon, text):
    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(icon, color="#ccffffff", size=18),
                ft.Text(text, color="#ccffffff", size=13),
            ],
            spacing=8,
        ),
        bgcolor="#15ffffff",
        border_radius=30,
        padding=ft.padding.symmetric(horizontal=20, vertical=10),
    )
