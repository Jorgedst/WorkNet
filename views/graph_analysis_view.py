"""
Rol 5 — Integrador y Analista de Visualización
Vista de Análisis de Red: conecta los botones del frontend con las
5 consultas Cypher del Especialista en Grafos (graph_queries.py).
"""

import threading
import flet as ft
from utils.colors import (
    BG_CARD, BG_INPUT, BG_PRIMARY, BG_SECONDARY,
    TEXT_PRIMARY, TEXT_SECONDARY,
    ACCENT_PRIMARY, ACCENT_SUCCESS, ACCENT_WARNING, BORDER_COLOR,
)
from services import graph_queries
from services.connection import get_driver


# ── Colores de estado ─────────────────────────────────────────────────────────
COLOR_BADGE = {
    "habilidades": "#7c3aed",
    "contactos":   "#0891b2",
    "ruta":        "#059669",
    "candidatos":  "#d97706",
    "proyectos":   "#e11d48",
}


# ── Helpers de UI ─────────────────────────────────────────────────────────────

def _field(label: str, hint: str = "", width: int = 280) -> ft.TextField:
    """Campo de texto con estilo consistente con el resto de la app."""
    return ft.TextField(
        label=label,
        hint_text=hint,
        border_color=BORDER_COLOR,
        focused_border_color=ACCENT_PRIMARY,
        bgcolor=BG_INPUT,
        color=TEXT_PRIMARY,
        label_style=ft.TextStyle(color=TEXT_SECONDARY),
        hint_style=ft.TextStyle(color=TEXT_SECONDARY, size=11),
        cursor_color=ACCENT_PRIMARY,
        border_radius=10,
        text_size=13,
        height=48,
        width=width,
    )


def _chip(text: str, color: str) -> ft.Container:
    """Chip de resultado con color temático."""
    return ft.Container(
        content=ft.Text(text, color=TEXT_PRIMARY, size=12, weight=ft.FontWeight.W_500),
        bgcolor=color + "30",
        border=ft.border.all(1, color + "60"),
        border_radius=20,
        padding=ft.padding.symmetric(horizontal=12, vertical=5),
    )


def _badge(text: str, color: str) -> ft.Container:
    """Badge de encabezado de tarjeta."""
    return ft.Container(
        content=ft.Text(text, color=color, size=10, weight=ft.FontWeight.W_600),
        bgcolor=color + "25",
        border=ft.border.all(1, color + "50"),
        border_radius=20,
        padding=ft.padding.symmetric(horizontal=10, vertical=4),
    )


def _divider_row() -> ft.Divider:
    return ft.Divider(height=1, color=BORDER_COLOR)


# ── Componente principal de tarjeta de consulta ───────────────────────────────

def _query_card(
    page: ft.Page,
    numero: str,
    titulo: str,
    descripcion: str,
    badge_label: str,
    badge_color: str,
    icon: str,
    inputs: list,          # lista de ft.TextField
    on_execute,            # función que recibe los valores y retorna resultados
    build_results,         # función que recibe los resultados y retorna ft.Control
) -> ft.Container:
    """
    Tarjeta reutilizable para cada consulta de grafo.
    Maneja 4 estados: idle → loading → results / error.
    """

    # ── Estado de la tarjeta ──────────────────────────────────────────────────
    result_area = ft.Column(spacing=8, visible=False)
    loading_ring = ft.ProgressRing(
        width=24, height=24, stroke_width=2,
        color=badge_color, visible=False,
    )
    status_text = ft.Text("", color=TEXT_SECONDARY, size=12, italic=True)
    execute_btn_text = ft.Text(
        "Ejecutar", color=TEXT_PRIMARY, size=13, weight=ft.FontWeight.W_500,
    )
    execute_btn = ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(ft.Icons.PLAY_ARROW_ROUNDED, color=TEXT_PRIMARY, size=16),
                execute_btn_text,
            ],
            spacing=6,
            tight=True,
        ),
        bgcolor=badge_color,
        border_radius=10,
        padding=ft.padding.symmetric(horizontal=18, vertical=10),
        ink=True,
        animate=ft.Animation(150, ft.AnimationCurve.EASE_IN_OUT),
    )

    def set_loading(is_loading: bool):
        loading_ring.visible = is_loading
        execute_btn.disabled = is_loading
        execute_btn_text.value = "Ejecutando..." if is_loading else "Ejecutar"
        execute_btn.bgcolor = badge_color + "80" if is_loading else badge_color

    def run_query(e):
        # Validar que los campos no estén vacíos
        values = [f.value.strip() if f.value else "" for f in inputs]
        if any(v == "" for v in values):
            status_text.value = "⚠ Completa todos los campos antes de ejecutar."
            status_text.color = ACCENT_WARNING
            result_area.visible = False
            result_area.controls.clear()
            page.update()
            return

        # Estado: cargando
        set_loading(True)
        status_text.value = "Consultando Neo4j..."
        status_text.color = TEXT_SECONDARY
        result_area.visible = False
        result_area.controls.clear()
        page.update()

        def _worker():
            try:
                driver = get_driver()
                results = on_execute(driver, *values)

                # Construir controles de resultados
                if results:
                    controls = build_results(results)
                    result_area.controls = [
                        ft.Text(
                            f"✓  {len(results) if isinstance(results, list) else 1} resultado(s) encontrado(s)",
                            color=ACCENT_SUCCESS, size=12, weight=ft.FontWeight.W_500,
                        ),
                        _divider_row(),
                        *controls,
                    ]
                    status_text.value = ""
                else:
                    result_area.controls = [
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Icon(ft.Icons.SEARCH_OFF_ROUNDED,
                                            color=TEXT_SECONDARY, size=32),
                                    ft.Text("Sin resultados para los parámetros ingresados.",
                                            color=TEXT_SECONDARY, size=13),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=8,
                            ),
                            alignment=ft.Alignment(0, 0),
                            padding=20,
                        )
                    ]
                    status_text.value = ""

                result_area.visible = True

            except Exception as ex:
                result_area.controls = [
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Icon(ft.Icons.WIFI_OFF_ROUNDED,
                                        color="#ef4444", size=32),
                                ft.Text("Error de conexión con Neo4j",
                                        color="#ef4444", size=13,
                                        weight=ft.FontWeight.W_600),
                                ft.Text(str(ex)[:180],
                                        color=TEXT_SECONDARY, size=11),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=6,
                        ),
                        alignment=ft.Alignment(0, 0),
                        padding=20,
                    )
                ]
                result_area.visible = True
                status_text.value = ""

            finally:
                set_loading(False)
                # Use individual control updates which are more reliable from threads
                try:
                    loading_ring.update()
                except Exception:
                    pass
                try:
                    execute_btn.update()
                except Exception:
                    pass
                try:
                    status_text.update()
                except Exception:
                    pass
                try:
                    result_area.update()
                except Exception:
                    pass

        threading.Thread(target=_worker, daemon=True).start()

    execute_btn.on_click = run_query

    # ── Layout de la tarjeta ──────────────────────────────────────────────────
    return ft.Container(
        content=ft.Column(
            controls=[
                # Encabezado
                ft.Row(
                    controls=[
                        ft.Container(
                            content=ft.Text(numero, color=badge_color, size=13,
                                            weight=ft.FontWeight.BOLD),
                            bgcolor=badge_color + "20",
                            border_radius=8,
                            width=32, height=32,
                            alignment=ft.Alignment(0, 0),
                        ),
                        ft.Column(
                            controls=[
                                ft.Row(
                                    controls=[
                                        ft.Text(titulo, color=TEXT_PRIMARY, size=15,
                                                weight=ft.FontWeight.W_600),
                                        _badge(badge_label, badge_color),
                                    ],
                                    spacing=8,
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                ),
                                ft.Text(descripcion, color=TEXT_SECONDARY, size=12),
                            ],
                            spacing=2,
                            expand=True,
                        ),
                        ft.Icon(icon, color=badge_color + "80", size=28),
                    ],
                    spacing=12,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                _divider_row(),
                # Inputs + botón ejecutar
                ft.Row(
                    controls=[
                        *inputs,
                        ft.Column(
                            controls=[
                                ft.Container(height=4),
                                ft.Row(
                                    controls=[execute_btn, loading_ring],
                                    spacing=10,
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                ),
                            ],
                            spacing=0,
                        ),
                    ],
                    spacing=12,
                    wrap=True,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                status_text,
                # Área de resultados
                result_area,
            ],
            spacing=14,
        ),
        bgcolor=BG_CARD,
        border_radius=16,
        border=ft.border.all(1, BORDER_COLOR),
        padding=ft.padding.symmetric(horizontal=20, vertical=18),
        animate=ft.Animation(200, ft.AnimationCurve.EASE_IN_OUT),
    )


# ── Constructores de resultados ───────────────────────────────────────────────

def _build_similar_skills_results(results: list) -> list:
    """Tarjeta 1: Usuarios con habilidades similares."""
    controls = []
    for row in results:
        usuario = row.get("usuario", "—")
        comunes = row.get("habilidades_comunes", [])
        total = row.get("total_comunes", 0)
        controls.append(ft.Container(
            content=ft.Row(
                controls=[
                    ft.CircleAvatar(
                        content=ft.Text(
                            "".join(p[0].upper() for p in usuario.split()[:2]),
                            size=12, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY,
                        ),
                        bgcolor="#7c3aed", radius=20,
                    ),
                    ft.Column(
                        controls=[
                            ft.Text(usuario, color=TEXT_PRIMARY, size=13,
                                    weight=ft.FontWeight.W_600),
                            ft.Row(
                                controls=[_chip(h, "#7c3aed") for h in comunes[:5]],
                                spacing=4, wrap=True,
                            ),
                        ],
                        spacing=4, expand=True,
                    ),
                    ft.Container(
                        content=ft.Text(f"{total} en común", color="#7c3aed",
                                        size=12, weight=ft.FontWeight.W_600),
                        bgcolor="#7c3aed20", border_radius=20,
                        padding=ft.padding.symmetric(horizontal=10, vertical=4),
                    ),
                ],
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=BG_PRIMARY, border_radius=10,
            border=ft.border.all(1, BORDER_COLOR), padding=12,
        ))
    return controls


def _build_common_contacts_results(results: list) -> list:
    """Tarjeta 2: Contactos en común."""
    controls = []
    for row in results:
        nombre = row.get("contacto_comun", "—")
        cargo = row.get("cargo", "—")
        controls.append(ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.PERSON_ROUNDED, color="#0891b2", size=20),
                    ft.Column(
                        controls=[
                            ft.Text(nombre, color=TEXT_PRIMARY, size=13,
                                    weight=ft.FontWeight.W_600),
                            ft.Text(cargo or "—", color=TEXT_SECONDARY, size=11),
                        ],
                        spacing=2, expand=True,
                    ),
                    ft.Container(
                        content=ft.Text("Contacto común", color="#0891b2", size=11),
                        bgcolor="#0891b220", border_radius=20,
                        padding=ft.padding.symmetric(horizontal=10, vertical=4),
                    ),
                ],
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=BG_PRIMARY, border_radius=10,
            border=ft.border.all(1, BORDER_COLOR), padding=12,
        ))
    return controls


def _build_shortest_path_results(result) -> list:
    """Tarjeta 3: Ruta más corta — result es un dict {ruta, pasos}."""
    if isinstance(result, list):
        result = result[0] if result else {}

    ruta = result.get("ruta", [])
    pasos = result.get("pasos", -1)
    mensaje = result.get("mensaje", "")

    if mensaje or pasos == -1:
        return [ft.Text(mensaje or "Sin ruta encontrada.",
                        color=TEXT_SECONDARY, size=13)]

    # Visualización de la ruta como nodos conectados
    nodo_controls = []
    for i, nodo in enumerate(ruta):
        nodo_controls.append(ft.Container(
            content=ft.Text(nodo or "?", color=TEXT_PRIMARY, size=12,
                            weight=ft.FontWeight.W_500),
            bgcolor="#05966930", border=ft.border.all(1, "#05966970"),
            border_radius=20,
            padding=ft.padding.symmetric(horizontal=14, vertical=6),
        ))
        if i < len(ruta) - 1:
            nodo_controls.append(
                ft.Icon(ft.Icons.ARROW_FORWARD_ROUNDED, color="#059669", size=16)
            )

    return [
        ft.Container(
            content=ft.Text(f"Longitud de ruta: {pasos} salto(s)",
                            color=ACCENT_SUCCESS, size=12, weight=ft.FontWeight.W_600),
            bgcolor=ACCENT_SUCCESS + "15", border_radius=8,
            padding=ft.padding.symmetric(horizontal=12, vertical=6),
        ),
        ft.Row(
            controls=nodo_controls,
            wrap=True, spacing=6, run_spacing=6,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    ]


def _build_candidates_results(results: list) -> list:
    """Tarjeta 4: Candidatos para una oferta."""
    controls = []
    for i, row in enumerate(results):
        candidato = row.get("candidato", "—")
        email = row.get("email", "")
        habilidades = row.get("habilidades_match", 0)
        conexiones = row.get("conexiones_internas", 0)
        puntaje = row.get("puntaje", 0)
        medal_color = ["#fbbf24", "#94a3b8", "#cd7c32"][i] if i < 3 else TEXT_SECONDARY
        controls.append(ft.Container(
            content=ft.Row(
                controls=[
                    ft.Container(
                        content=ft.Text(f"#{i+1}", color=medal_color, size=13,
                                        weight=ft.FontWeight.BOLD),
                        width=32, alignment=ft.Alignment(0, 0),
                    ),
                    ft.CircleAvatar(
                        content=ft.Text(
                            "".join(p[0].upper() for p in candidato.split()[:2]),
                            size=11, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY,
                        ),
                        bgcolor="#d97706", radius=18,
                    ),
                    ft.Column(
                        controls=[
                            ft.Text(candidato, color=TEXT_PRIMARY, size=13,
                                    weight=ft.FontWeight.W_600),
                            ft.Text(email, color=TEXT_SECONDARY, size=11),
                            ft.Row(controls=[
                                _chip(f"{habilidades} habilidades", "#d97706"),
                                _chip(f"{conexiones} conexiones internas", "#d97706"),
                            ], spacing=6),
                        ],
                        spacing=3, expand=True,
                    ),
                    ft.Container(
                        content=ft.Text(f"Puntaje: {puntaje}", color="#d97706",
                                        size=13, weight=ft.FontWeight.BOLD),
                        bgcolor="#d9770620", border_radius=10,
                        padding=ft.padding.symmetric(horizontal=12, vertical=6),
                    ),
                ],
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=BG_PRIMARY, border_radius=10,
            border=ft.border.all(1, BORDER_COLOR), padding=12,
        ))
    return controls


def _build_related_projects_results(results: list) -> list:
    """Tarjeta 5: Proyectos relacionados."""
    if not results:
        return [ft.Text("No se encontraron proyectos relacionados.",
                        color=TEXT_SECONDARY, size=13)]
    controls = []
    seen = set()
    for item in results:
        nombre = item.get("proyecto") or item.get("name", "—")
        vinculo = item.get("vinculo", "relacionado")
        if nombre in seen:
            continue
        seen.add(nombre)
        vinculo_color = "#e11d48" if "miembro" in vinculo else "#7c3aed"
        controls.append(ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.FOLDER_ROUNDED, color="#e11d48", size=18),
                    ft.Column(
                        controls=[
                            ft.Text(nombre, color=TEXT_PRIMARY, size=13,
                                    weight=ft.FontWeight.W_600),
                            ft.Text(f"Vínculo: {vinculo}", color=TEXT_SECONDARY, size=11),
                        ],
                        spacing=2, expand=True,
                    ),
                    ft.Container(
                        content=ft.Text(vinculo, color=vinculo_color, size=11),
                        bgcolor=vinculo_color + "20", border_radius=20,
                        padding=ft.padding.symmetric(horizontal=10, vertical=4),
                    ),
                ],
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=BG_PRIMARY, border_radius=10,
            border=ft.border.all(1, BORDER_COLOR), padding=12,
        ))
    return controls


# ── Vista pública ─────────────────────────────────────────────────────────────

def graph_analysis_content(page: ft.Page, on_view_profile=None) -> ft.Column:
    """
    Vista principal del Rol 5.
    Muestra las 5 tarjetas de análisis de grafos conectadas a Neo4j
    a través de graph_queries.py.
    """

    header = ft.Row(
        controls=[
            ft.Container(
                content=ft.Icon(ft.Icons.ANALYTICS_ROUNDED,
                                color=ACCENT_PRIMARY, size=26),
                bgcolor=ACCENT_PRIMARY + "20",
                border_radius=12, padding=10,
            ),
            ft.Column(
                controls=[
                    ft.Text("Análisis de Red", color=TEXT_PRIMARY,
                            size=24, weight=ft.FontWeight.BOLD),
                    ft.Text("Consultas Cypher sobre el grafo de Neo4j en tiempo real",
                            color=TEXT_SECONDARY, size=13),
                ],
                spacing=2, expand=True,
            ),
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.CIRCLE_ROUNDED, color=ACCENT_SUCCESS, size=10),
                        ft.Text("Neo4j Aura", color=TEXT_SECONDARY, size=12),
                    ],
                    spacing=6,
                ),
                bgcolor=BG_SECONDARY, border_radius=20,
                border=ft.border.all(1, BORDER_COLOR),
                padding=ft.padding.symmetric(horizontal=14, vertical=8),
            ),
        ],
        spacing=14,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    # ── Tarjeta 1: Habilidades similares ─────────────────────────────────────
    email_q1 = _field("Email del usuario", "ej: ruiz@gmail.com", width=300)
    card1 = _query_card(
        page=page,
        numero="01",
        titulo="Usuarios con habilidades similares",
        descripcion="¿Quién tiene habilidades en común con este usuario?",
        badge_label="HABILIDADES",
        badge_color=COLOR_BADGE["habilidades"],
        icon=ft.Icons.PEOPLE_ALT_ROUNDED,
        inputs=[email_q1],
        on_execute=lambda driver, email: graph_queries.usuarios_con_habilidades_similares(driver, email),
        build_results=_build_similar_skills_results,
    )

    # ── Tarjeta 2: Contactos en común ────────────────────────────────────────
    email_q2a = _field("Email profesional A", "ej: ruiz@gmail.com", width=260)
    email_q2b = _field("Email profesional B", "ej: roncayomesas@gmail.com", width=260)
    card2 = _query_card(
        page=page,
        numero="02",
        titulo="Contactos en común",
        descripcion="¿Qué contactos comparten dos profesionales?",
        badge_label="RED",
        badge_color=COLOR_BADGE["contactos"],
        icon=ft.Icons.CONNECT_WITHOUT_CONTACT_ROUNDED,
        inputs=[email_q2a, email_q2b],
        on_execute=lambda driver, ea, eb: graph_queries.contactos_en_comun(driver, ea, eb),
        build_results=_build_common_contacts_results,
    )

    # ── Tarjeta 3: Ruta más corta ─────────────────────────────────────────────
    email_q3 = _field("Email del usuario", "ej: ruiz@gmail.com", width=260)
    empresa_q3 = _field("Nombre de la empresa", "ej: TechCorp", width=220)

    def _run_ruta(driver, email, empresa):
        result = graph_queries.ruta_mas_corta(driver, email, empresa)
        # Normalizar: la función retorna un dict, no una lista
        return [result] if result.get("pasos", -1) != -1 else []

    card3 = _query_card(
        page=page,
        numero="03",
        titulo="Ruta más corta a una empresa",
        descripcion="¿Cuál es el camino más corto en el grafo entre un usuario y una empresa?",
        badge_label="RUTA",
        badge_color=COLOR_BADGE["ruta"],
        icon=ft.Icons.ALT_ROUTE_ROUNDED,
        inputs=[email_q3, empresa_q3],
        on_execute=_run_ruta,
        build_results=_build_shortest_path_results,
    )

    # ── Tarjeta 4: Candidatos para oferta ─────────────────────────────────────
    oferta_q4 = _field("Título exacto de la oferta", "ej: Senior Python Developer", width=340)
    card4 = _query_card(
        page=page,
        numero="04",
        titulo="Candidatos recomendados para una oferta",
        descripcion="¿Quiénes son los mejores candidatos según habilidades y conexiones?",
        badge_label="CANDIDATOS",
        badge_color=COLOR_BADGE["candidatos"],
        icon=ft.Icons.STAR_ROUNDED,
        inputs=[oferta_q4],
        on_execute=lambda driver, oferta: graph_queries.candidatos_para_oferta(driver, oferta),
        build_results=_build_candidates_results,
    )

    # ── Tarjeta 5: Proyectos relacionados ─────────────────────────────────────
    proyecto_q5 = _field("Nombre exacto del proyecto", "ej: AI Recommendation Engine", width=340)
    card5 = _query_card(
        page=page,
        numero="05",
        titulo="Proyectos relacionados",
        descripcion="¿Qué proyectos comparten miembros o tecnologías con este proyecto?",
        badge_label="PROYECTOS",
        badge_color=COLOR_BADGE["proyectos"],
        icon=ft.Icons.SCHEMA_ROUNDED,
        inputs=[proyecto_q5],
        on_execute=lambda driver, proyecto: graph_queries.proyectos_relacionados(driver, proyecto),
        build_results=_build_related_projects_results,
    )

    return ft.Column(
        controls=[
            header,
            ft.Container(height=4),
            card1,
            card2,
            card3,
            card4,
            card5,
            ft.Container(height=16),
        ],
        spacing=14,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )
