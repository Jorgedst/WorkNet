"""
WorkNet - Professional Network Application
Main entry point with routing and layout management.
"""

import flet as ft
from utils.colors import BG_PRIMARY, BG_SECONDARY, BORDER_COLOR
from components.sidebar import create_sidebar
from views import (
    login_view, register_view, dashboard_content,
    network_content, companies_content, projects_content,
    jobs_content, profile_content, settings_content, company_register_view
)
from services.graph_service import GraphService


def main(page: ft.Page):
    page.title = "WorkNet"
    page.window.width = 1290
    page.window.height = 720
    page.window.min_width = 1100
    page.window.min_height = 600
    page.window.alignment = ft.Alignment(0, 0)
    page.window.maximized = True
    page.bgcolor = BG_PRIMARY
    page.padding = 0
    page.spacing = 0

    page.fonts = {
        "Inter": "Inter-VariableFont_opsz,wght.ttf"
    }
    page.theme = ft.Theme(
        font_family="Inter",
        color_scheme_seed=ft.Colors.BLUE,
    )

    service = GraphService()

    def get_active_route():
        """Extract the sub-route from the full route."""
        route = page.route or "/"
        if route.startswith("/app/"):
            return route.replace("/app/", "").split("/")[0]
        return route

    def navigate(route_name):
        """Navigate to a sub-route within the app."""
        page.go(f"/app/{route_name}")

    def view_profile(user_id):
        """Navigate to a user's profile."""
        page.go(f"/app/profile/{user_id}")

    def build_app_layout(content_builder):
        """Build the main app layout with sidebar and content area."""
        current_user = service.get_current_user()
        active = get_active_route()

        sidebar = create_sidebar(
            page=page,
            active_route=active,
            on_navigate=navigate,
            current_user=current_user,
        )

        content = content_builder()

        return ft.View(
            route=page.route,
            controls=[
                ft.Row(
                    controls=[
                        sidebar,
                        ft.Container(
                            content=content,
                            expand=True,
                            padding=24,
                        ),
                    ],
                    spacing=0,
                    expand=True,
                ),
            ],
            bgcolor=BG_PRIMARY,
            padding=0,
            spacing=0,
        )

    def route_change(e):
        page.views.clear()
        route = page.route or "/"

        if route == "/":
            page.views.append(login_view(page))
        elif route == "/register":
            page.views.append(register_view(page))
        elif route == "/register-company":
            page.views.append(company_register_view(page))
        elif route.startswith("/app/"):
            # Check if user is logged in
            user_id = service.current_user_id
            if not user_id:
                page.views.append(login_view(page))
                page.update()
                return

            sub_route = get_active_route()

            if sub_route == "dashboard":
                page.views.append(build_app_layout(
                    lambda: dashboard_content(page, on_view_profile=view_profile)
                ))
            elif sub_route == "network":
                page.views.append(build_app_layout(
                    lambda: network_content(page, on_view_profile=view_profile)
                ))
            elif sub_route == "projects":
                page.views.append(build_app_layout(
                    lambda: projects_content(page, on_view_profile=view_profile)
                ))
            elif sub_route == "jobs":
                page.views.append(build_app_layout(
                    lambda: jobs_content(page, on_view_profile=view_profile)
                ))
            elif sub_route == "companies":
                page.views.append(build_app_layout(
                    lambda: companies_content(page, on_view_profile=view_profile)
                ))
            elif sub_route == "settings":
                page.views.append(build_app_layout(
                    lambda: settings_content(page, on_view_profile=view_profile)
                ))
            elif sub_route == "profile":
                # Extract user_id from route: /app/profile/{user_id}
                parts = route.split("/")
                profile_uid = parts[-1] if len(parts) > 3 else None
                page.views.append(build_app_layout(
                    lambda uid=profile_uid: profile_content(page, user_id=uid,
                                                            on_view_profile=view_profile)
                ))
            else:
                page.views.append(build_app_layout(
                    lambda: dashboard_content(page, on_view_profile=view_profile)
                ))
        else:
            page.views.append(login_view(page))

        page.update()

    def view_pop(e):
        page.views.pop()
        if page.views:
            top_view = page.views[-1]
            page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    route_change(None)


if __name__ == "__main__":
    ft.run(main, assets_dir="assets")
