"""Grafo visual simple — Usuarios, Empresas y Ofertas."""

import flet as ft
import math
from utils.colors import BG_GRAPH, TEXT_PRIMARY, TEXT_SECONDARY, BORDER_COLOR

EDGE_COLORS = {
    "CONECTA_CON": "#2563eb60",
    "TRABAJA_EN":  "#05966960",
    "PUBLICA":     "#e11d4860",
}

NODE_CONFIG = {
    "user":    {"size": 26, "border": 2},
    "company": {"size": 32, "border": 3},
    "job":     {"size": 22, "border": 2},
}


def network_graph(graph_data: dict, width: float = 420, height: float = 500, on_node_click=None):
    nodes = graph_data.get("nodes", [])
    edges = graph_data.get("edges", [])

    if not nodes:
        return ft.Container(
            content=ft.Text("No hay datos de red", color=TEXT_SECONDARY),
            alignment=ft.Alignment(0, 0), width=width, height=height,
        )

    inner_w = width - 40
    inner_h = height - 60
    positions = _calculate_positions(nodes, inner_w, inner_h)
    node_map = {n["id"]: i for i, n in enumerate(nodes)}

    # Aristas
    edge_controls = []
    for edge in edges:
        fi = node_map.get(edge["from"])
        ti = node_map.get(edge["to"])
        if fi is not None and ti is not None:
            x1, y1 = positions[fi]
            x2, y2 = positions[ti]
            r = NODE_CONFIG.get(nodes[fi]["type"], {"size": 26})["size"]
            color = EDGE_COLORS.get(edge["type"], "#ffffff20")
            line = _create_line(x1 + r, y1 + r, x2 + r, y2 + r, color)
            if line:
                edge_controls.append(line)

    # Nodos
    node_controls = []
    for i, node in enumerate(nodes):
        x, y = positions[i]
        cfg = NODE_CONFIG.get(node["type"], {"size": 26, "border": 2})
        size = cfg["size"]
        color = node.get("color", "#4f46e5")
        label = node["label"]

        if node["type"] == "company":
            icon = ft.Icon(ft.Icons.BUSINESS_ROUNDED, color="#ffffff", size=size * 0.55)
        elif node["type"] == "job":
            icon = ft.Icon(ft.Icons.WORK_ROUNDED, color="#ffffff", size=size * 0.55)
        else:
            parts = label.split()
            initials = "".join(p[0].upper() for p in parts[:2]) if parts else "?"
            icon = ft.Text(initials, size=8, weight=ft.FontWeight.BOLD, color="#ffffff")

        short_label = label.split()[0] if node["type"] == "user" else " ".join(label.split()[:2])

        node_controls.append(ft.Container(
            content=ft.Column(
                controls=[
                    ft.Container(
                        content=ft.CircleAvatar(content=icon, bgcolor=color, radius=size // 2),
                        border=ft.border.all(cfg["border"], color),
                        border_radius=50,
                        shadow=ft.BoxShadow(blur_radius=5, color=color + "40",
                                            spread_radius=1, offset=ft.Offset(0, 2)),
                    ),
                    ft.Text(short_label, color=TEXT_PRIMARY, size=7,
                            text_align=ft.TextAlign.CENTER,
                            max_lines=1, overflow=ft.TextOverflow.ELLIPSIS, width=58),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=2,
            ),
            left=x, top=y,
            on_click=lambda e, nid=node["id"]: on_node_click(nid) if on_node_click else None,
        ))

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Red de Conexiones", color=TEXT_PRIMARY, size=15,
                        weight=ft.FontWeight.W_600),
                ft.InteractiveViewer(
                    content=ft.Container(
                        content=ft.Stack(
                            controls=edge_controls + node_controls,
                            width=inner_w, height=inner_h,
                        ),
                        alignment=ft.Alignment(0, 0),
                    ),
                    expand=True,
                    max_scale=5.0, min_scale=0.2,
                    boundary_margin=ft.margin.all(800),
                ),
            ],
            spacing=8,
        ),
        bgcolor=BG_GRAPH, border_radius=16,
        border=ft.border.all(1, BORDER_COLOR),
        padding=16, expand=True,
    )


def _create_line(x1, y1, x2, y2, color):
    dx, dy = x2 - x1, y2 - y1
    length = math.sqrt(dx * dx + dy * dy)
    if length < 1:
        return None
    return ft.Container(
        width=length, height=1.5, bgcolor=color, border_radius=1,
        left=x1, top=y1,
        rotate=ft.Rotate(math.atan2(dy, dx), alignment=ft.Alignment(-1, 0)),
    )


def _calculate_positions(nodes, width, height):
    positions = [(0, 0)] * len(nodes)
    cx, cy = width / 2 - 20, height / 2 - 20

    # Empresas al centro, usuarios en medio, ofertas afuera
    order = ["company", "user", "job"]
    layers = []
    for t in order:
        layer = [(i, n) for i, n in enumerate(nodes) if n["type"] == t]
        if layer:
            layers.append(layer)

    max_r = min(width, height) * 0.42
    inner = max_r * 0.18
    step = (max_r - inner) / max(len(layers) - 1, 1)
    radii = [inner + step * i for i in range(len(layers))]

    for li, layer_nodes in enumerate(layers):
        radius = radii[li]
        count = max(len(layer_nodes), 1)
        for idx, (i, _) in enumerate(layer_nodes):
            angle = (2 * math.pi * idx / count) - math.pi / 2
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)
            positions[i] = (x, y)

    return positions