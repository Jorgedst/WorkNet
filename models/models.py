"""
Data models for WorkNet application.
These models represent the graph entities (nodes) and can be used
with both mock data and Neo4j integration.

Graph Nodes: User, Company, Skill, Project, JobOffer
Graph Relationships: Connection, WorksAt, Participation, Publication, Requirement
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class User:
    """Nodo: Usuario - Persona registrada en la plataforma."""
    id: str
    name: str
    email: str
    password: str = ""  # Hashed in production
    title: str = ""  # Professional title (e.g., "Senior Software Engineer")
    bio: str = ""
    avatar_color: str = "#2563eb"  # Color for avatar circle
    initials: str = ""  # For avatar display
    location: str = ""
    phone: str = ""
    skills: list = field(default_factory=list)  # List of skill names
    is_online: bool = False

    def __post_init__(self):
        if not self.initials and self.name:
            parts = self.name.split()
            self.initials = "".join(p[0].upper() for p in parts[:2])


@dataclass
class Company:
    """Nodo: Empresa - Organización o compañía."""
    id: str
    name: str
    description: str = ""
    industry: str = ""
    logo_color: str = "#7c3aed"  # Color for logo circle
    initials: str = ""
    location: str = ""
    website: str = ""
    employee_count: int = 0
    founded_year: int = 0

    def __post_init__(self):
        if not self.initials and self.name:
            self.initials = self.name[0].upper()


@dataclass
class Skill:
    """Nodo: Habilidad - Competencia o conocimiento."""
    id: str
    name: str
    category: str = ""  # e.g., "Programming", "Framework", "Soft Skill"


@dataclass
class Project:
    """Nodo: Proyecto - Trabajo o iniciativa desarrollada."""
    id: str
    name: str
    company_id: str = ""
    company_name: str = ""
    description: str = ""
    status: str = "Active"  # Active, Completed, On Hold
    technologies: list = field(default_factory=list)
    start_date: str = ""
    end_date: str = ""


@dataclass
class JobOffer:
    """Nodo: Oferta - Vacante laboral."""
    id: str
    title: str
    company_id: str
    company_name: str = ""
    project_id: str = ""
    project_name: str = ""
    description: str = ""
    location: str = ""
    salary_range: str = ""
    job_type: str = "Full-time"  # Full-time, Part-time, Contract, Remote
    required_skills: list = field(default_factory=list)
    posted_date: str = ""
    is_active: bool = True
    experience_level: str = ""  # Junior, Mid, Senior


@dataclass
class Connection:
    """Relación: CONECTA_CON - Relación entre usuarios."""
    user_id_1: str
    user_id_2: str
    connection_type: str = "professional"  # professional, colleague, classmate
    connected_since: str = ""
    status: str = "accepted"  # pending, accepted, rejected


@dataclass
class WorksAt:
    """Relación: TRABAJA_EN - Usuario vinculado a empresa."""
    user_id: str
    company_id: str
    role: str = ""
    start_date: str = ""
    end_date: Optional[str] = None  # None = currently working
    is_current: bool = True


@dataclass
class Participation:
    """Relación: PARTICIPA_EN - Usuario que participa en un proyecto."""
    user_id: str
    project_id: str
    role: str = ""  # Lead, Member, Contributor


@dataclass
class Publication:
    """Relación: PUBLICA - Empresa que publica una oferta."""
    company_id: str
    job_id: str
    published_date: str = ""


@dataclass
class Requirement:
    """Relación: REQUIERE - Oferta que requiere una habilidad."""
    job_id: str
    skill_id: str
    level: str = "Required"  # Required, Preferred, Nice-to-have
