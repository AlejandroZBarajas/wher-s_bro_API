"""
Core
Componentes centrales de la aplicación.
"""

from app.core.config import settings
from app.core.room_manager import room_manager

__all__ = ["settings", "room_manager"]