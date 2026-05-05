"""Reusable skill tag chip component."""

import flet as ft
from utils.colors import get_skill_color


def skill_tag(name: str, size: str = "small"):
    """Create a colored skill tag chip."""
    colors = get_skill_color(name)
    font_size = 10 if size == "small" else 12
    h_pad = 8 if size == "small" else 12
    v_pad = 3 if size == "small" else 5

    return ft.Container(
        content=ft.Text(name, color=colors["text"], size=font_size, weight=ft.FontWeight.W_500),
        bgcolor=colors["bg"],
        border=ft.border.all(1, colors["border"]),
        border_radius=6,
        padding=ft.padding.symmetric(horizontal=h_pad, vertical=v_pad),
    )
