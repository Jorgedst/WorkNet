# Views package

from .login_view import login_view
from .register_view import register_view
from .dashboard_view import dashboard_content
from .network_view import network_content
from .companies_view import companies_content
from .projects_view import projects_content
from .jobs_view import jobs_content
from .profile_view import profile_content
from .settings_view import settings_content
from .company_register_view import company_register_view
from .graph_analysis_view import graph_analysis_content

__all__ = [
    "login_view", "register_view", "dashboard_content",
    "network_content", "companies_content", "projects_content",
    "jobs_content", "profile_content", "settings_content",
    "company_register_view", "graph_analysis_content",
]
