"""
Color palette and theme constants for WorkNet application.
Dark theme inspired by the ProNetwork design.
"""

# ── Background Colors ──────────────────────────────────────
BG_PRIMARY = "#0f1221"        # Main app background
BG_SECONDARY = "#161b2e"      # Sidebar background
BG_CARD = "#1c2240"           # Card background
BG_CARD_HOVER = "#232a4a"     # Card hover state
BG_INPUT = "#1a2038"          # Input field background
BG_HEADER = "#141929"         # Header area background
BG_GRAPH = "#141929"          # Graph panel background
BG_OVERLAY = "#0a0e1a"        # Modal overlay

# ── Accent Colors ──────────────────────────────────────────
ACCENT_PRIMARY = "#2563eb"     # Primary blue
ACCENT_PRIMARY_LIGHT = "#3b82f6"
ACCENT_SECONDARY = "#60a5fa"   # Light blue
ACCENT_HOVER = "#1d4ed8"       # Blue hover
ACCENT_SUCCESS = "#22c55e"     # Green (online, success)
ACCENT_WARNING = "#f59e0b"     # Warning/amber
ACCENT_DANGER = "#ef4444"      # Error/danger

# ── Text Colors ────────────────────────────────────────────
TEXT_PRIMARY = "#f0f6fc"       # Primary text (white-ish)
TEXT_SECONDARY = "#8b949e"     # Secondary/muted text
TEXT_MUTED = "#6e7681"         # Tertiary/muted text
TEXT_ACCENT = "#58a6ff"        # Accented text links

# ── Border & Divider ──────────────────────────────────────
BORDER_COLOR = "#2a3050"       # Default border
BORDER_LIGHT = "#21262d"       # Light border
DIVIDER_COLOR = "#1e2444"      # Divider lines

# ── Sidebar ───────────────────────────────────────────────
SIDEBAR_WIDTH = 240
SIDEBAR_ACTIVE_BG = "#2563eb"
SIDEBAR_HOVER_BG = "#1e2444"

# ── Gradient Colors ───────────────────────────────────────
GRADIENT_START = "#2563eb"
GRADIENT_END = "#7c3aed"

# ── Skill Tag Colors ─────────────────────────────────────
SKILL_COLORS = {
    "JavaScript":       {"bg": "#f7df1e20", "text": "#f7df1e", "border": "#f7df1e40"},
    "React":            {"bg": "#61dafb20", "text": "#61dafb", "border": "#61dafb40"},
    "Python":           {"bg": "#3776ab20", "text": "#6b9fd4", "border": "#3776ab40"},
    "Node.js":          {"bg": "#33993320", "text": "#5cb85c", "border": "#33993340"},
    "AI":               {"bg": "#ff6b6b20", "text": "#ff6b6b", "border": "#ff6b6b40"},
    "B2B":              {"bg": "#ff8c4220", "text": "#ff8c42", "border": "#ff8c4240"},
    "Java":             {"bg": "#b0721620", "text": "#e8a838", "border": "#b0721640"},
    "TypeScript":       {"bg": "#3178c620", "text": "#3178c6", "border": "#3178c640"},
    "Docker":           {"bg": "#2496ed20", "text": "#2496ed", "border": "#2496ed40"},
    "AWS":              {"bg": "#ff990020", "text": "#ff9900", "border": "#ff990040"},
    "SQL":              {"bg": "#e38d1320", "text": "#e38d13", "border": "#e38d1340"},
    "MongoDB":          {"bg": "#47a24820", "text": "#47a248", "border": "#47a24840"},
    "GraphQL":          {"bg": "#e535ab20", "text": "#e535ab", "border": "#e535ab40"},
    "Neo4j":            {"bg": "#008cc120", "text": "#008cc1", "border": "#008cc140"},
    "CSS":              {"bg": "#264de420", "text": "#6b8bea", "border": "#264de440"},
    "HTML":             {"bg": "#e3492620", "text": "#e34926", "border": "#e3492640"},
    "Git":              {"bg": "#f0503220", "text": "#f05032", "border": "#f0503240"},
    "Figma":            {"bg": "#a259ff20", "text": "#a259ff", "border": "#a259ff40"},
    "Machine Learning": {"bg": "#ff638420", "text": "#ff6384", "border": "#ff638440"},
    "Data Science":     {"bg": "#36a2eb20", "text": "#36a2eb", "border": "#36a2eb40"},
    "DevOps":           {"bg": "#00bfa520", "text": "#00bfa5", "border": "#00bfa540"},
    "Scrum":            {"bg": "#9c27b020", "text": "#ce93d8", "border": "#9c27b040"},
    "Agile":            {"bg": "#00968820", "text": "#4db6ac", "border": "#00968840"},
    "C++":              {"bg": "#00599c20", "text": "#649ad2", "border": "#00599c40"},
    "Rust":             {"bg": "#dea58420", "text": "#dea584", "border": "#dea58440"},
    "Go":               {"bg": "#00add820", "text": "#00add8", "border": "#00add840"},
    "Kotlin":           {"bg": "#7f52ff20", "text": "#7f52ff", "border": "#7f52ff40"},
    "Swift":            {"bg": "#fa722020", "text": "#fa7220", "border": "#fa722040"},
    "Flutter":          {"bg": "#02569b20", "text": "#54c5f8", "border": "#02569b40"},
}
DEFAULT_SKILL_COLOR = {"bg": "#8b949e20", "text": "#8b949e", "border": "#8b949e40"}


def get_skill_color(skill_name: str) -> dict:
    """Get color scheme for a skill tag."""
    return SKILL_COLORS.get(skill_name, DEFAULT_SKILL_COLOR)
