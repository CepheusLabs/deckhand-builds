"""Screen page handlers package.

Public API:
    PageContext  — shared context dataclass
    PageHandler  — abstract base for page handlers
    PageManager  — orchestrator (lifecycle, touch routing, status dispatch)
"""

from ._base import PageContext, PageHandler
from .manager import PageManager

__all__ = ["PageContext", "PageHandler", "PageManager"]
