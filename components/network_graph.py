"""Visual network graph component using Stack for nodes (no Canvas dependency)."""

import flet as ft
import math
from utils.colors import (
    BG_GRAPH, TEXT_PRIMARY, TEXT_SECONDARY, BORDER_COLOR, ACCENT_PRIMARY,
)


def network_graph(graph_data: dict, width: float = 420, height: float = 500, on_node_click=None):
    """
    Create a visual network graph panel using Stack-positioned containers.
    graph_data: {"nodes": [...], "edges": [...]}
    """
    nodes = graph_data.get("nodes", [])
    edges = graph_data.get("edges", [])

    if not nodes:
        return ft.Container(
            content=ft.Text("No hay datos de red", color=TEXT_SECONDARY),
            alignment=ft.Alignment(0, 0),
            width=width, height=height,
        )

    inner_w = width - 60
    inner_h = height - 120
    positions = _calculate_positions(nodes, inner_w, inner_h)
    node_map = {n["id"]: i for i, n in enumerate(nodes)}

    # Build edge lines using thin containers
    edge_controls = []
    for edge in edges:
        from_idx = node_map.get(edge["from"])
        to_idx = node_map.get(edge["to"])
        if from_idx is not None and to_idx is not None:
            x1, y1 = positions[from_idx]
            x2, y2 = positions[to_idx]
            # Create a line using a rotated container
            line = _create_line(x1 + 18, y1 + 18, x2 + 18, y2 + 18)
            if line:
                edge_controls.append(line)

    # Build node controls
    node_controls = []
    for i, node in enumerate(nodes):
        x, y = positions[i]
        is_company = node["type"] == "company"
        size = 36 if is_company else 32
        font_size = 9

        parts = node["label"].split()
        initials = "".join(p[0].upper() for p in parts[:2]) if parts else "?"

        node_container = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Container(
                        content=ft.CircleAvatar(
                            content=ft.Text(initials, size=font_size, weight=ft.FontWeight.BOLD,
                                            color="#ffffff" if is_company else TEXT_PRIMARY),
                            bgcolor="#000000" if is_company else node["color"],
                            radius=size // 2,
                        ),
                        border=ft.border.all(2, node["color"]),
                        border_radius=50,
                        padding=1,
                    ),
                    ft.Text(
                        node["label"], color=TEXT_PRIMARY, size=8,
                        text_align=ft.TextAlign.CENTER,
                        max_lines=1, overflow=ft.TextOverflow.ELLIPSIS,
                        width=65,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=2,
            ),
            left=x, top=y,
            on_click=lambda e, nid=node["id"]: on_node_click(nid) if on_node_click else None,
        )
        node_controls.append(node_container)

    graph_stack = ft.Stack(
        controls=edge_controls + node_controls,
        width=inner_w,
        height=inner_h,
    )

    zoom_level = [1.0]

    def handle_zoom_in(e):
        zoom_level[0] += 0.2
        graph_stack.scale = zoom_level[0]
        graph_stack.update()

    def handle_zoom_out(e):
        zoom_level[0] = max(0.2, zoom_level[0] - 0.2)
        graph_stack.scale = zoom_level[0]
        graph_stack.update()

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text("Grafo Visual de Red", color=TEXT_PRIMARY, size=16,
                                weight=ft.FontWeight.W_600),
                        ft.Container(expand=True),
                    ],
                ),
                ft.InteractiveViewer(
                    content=ft.Container(content=graph_stack, alignment=ft.Alignment(0, 0)),
                    expand=True,
                    max_scale=5.0,
                    min_scale=0.2,
                    boundary_margin=ft.margin.all(800),
                ),
                ft.Row(
                    controls=[
                        ft.Container(expand=True),
                        ft.Row(
                            controls=[
                                ft.IconButton(ft.Icons.ADD_ROUNDED, icon_color=TEXT_SECONDARY, icon_size=16, on_click=handle_zoom_in),
                                ft.IconButton(ft.Icons.REMOVE_ROUNDED, icon_color=TEXT_SECONDARY, icon_size=16, on_click=handle_zoom_out),
                            ],
                            spacing=0,
                        ),
                    ],
                ),
            ],
            spacing=8,
        ),
        bgcolor=BG_GRAPH,
        border_radius=16,
        border=ft.border.all(1, BORDER_COLOR),
        padding=16,
        expand=True,
    )


def _create_line(x1, y1, x2, y2):
    """Create a line between two points using a positioned/rotated thin container."""
    dx = x2 - x1
    dy = y2 - y1
    length = math.sqrt(dx * dx + dy * dy)
    if length < 1:
        return None
    angle = math.atan2(dy, dx)

    return ft.Container(
        width=length,
        height=2,
        bgcolor="#2563eb30",
        border_radius=1,
        left=x1,
        top=y1,
        rotate=ft.Rotate(angle, alignment=ft.Alignment(-1, 0)),
    )


def _calculate_positions(nodes, width, height):
    """Calculate node positions in concentric circles."""
    positions = [None] * len(nodes)
    cx, cy = width / 2 - 20, height / 2 - 20

    users = [(i, n) for i, n in enumerate(nodes) if n["type"] == "user"]
    companies = [(i, n) for i, n in enumerate(nodes) if n["type"] == "company"]

    r_inner = min(width, height) * 0.25
    for idx, (i, _) in enumerate(users):
        angle = (2 * math.pi * idx / max(len(users), 1)) - math.pi / 2
        x = cx + r_inner * math.cos(angle)
        y = cy + r_inner * math.sin(angle)
        positions[i] = (x, y)

    r_outer = min(width, height) * 0.40
    for idx, (i, _) in enumerate(companies):
        angle = (2 * math.pi * idx / max(len(companies), 1)) - math.pi / 4
        x = cx + r_outer * math.cos(angle)
        y = cy + r_outer * math.sin(angle)
        positions[i] = (x, y)

    return positions
