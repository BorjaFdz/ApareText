"""
ApareText Core Module

Motor central de snippets, parser de plantillas y gestión de base de datos.
"""

__version__ = "0.1.0"

from core.models import Snippet, SnippetVariable, Settings
from core.database import Database, get_db
from core.snippet_manager import SnippetManager
from core.template_parser import TemplateParser

__all__ = [
    "Snippet",
    "SnippetVariable",
    "Settings",
    "Database",
    "get_db",
    "SnippetManager",
    "TemplateParser",
]
