from typing import Dict, Optional
from datetime import datetime, timedelta
from app.models.room import Room, RoomUser
from app.core.config import settings
import asyncio
import logging

logger = logging.getLogger(__name__)


class RoomManager:
    """
    Gestor centralizado de salas activas en memoria.
    Maneja la limpieza automática de salas vacías.
    """
    
    def __init__(self):
        self.rooms: Dict[str, Room] = {}
        self.user_to_room: Dict[int, str] = {}  # Mapeo user_id -> room_code
        self._cleanup_task: Optional[asyncio.Task] = None
    
    def create_room(self, code: str) -> Room:
        """Crea una nueva sala"""
        now = datetime.utcnow()
        room = Room(
            code=code,
            created_at=now,
            last_activity=now,
            users=[]
        )
        self.rooms[code] = room
        logger.info(f"Sala creada: {code}")
        return room
    
    def get_room(self, code: str) -> Optional[Room]:
        """Obtiene una sala por su código"""
        return self.rooms.get(code)
    
    def room_exists(self, code: str) -> bool:
        """Verifica si existe una sala con el código dado"""
        return code in self.rooms
    
    def add_user_to_room(self, code: str, user_id: int, username: str) -> bool:
        """
        Agrega un usuario a una sala.
        
        Returns:
            bool: True si se agregó exitosamente, False si la sala no existe
        """
        room = self.get_room(code)
        if not room:
            return False
        
        # Remover usuario de sala anterior si existe
        self.remove_user_from_current_room(user_id)
        
        # Verificar si el usuario ya está en la sala
        if any(u.user_id == user_id for u in room.users):
            logger.warning(f"Usuario {user_id} ya está en sala {code}")
            return True
        
        # Agregar usuario
        room_user = RoomUser(
            user_id=user_id,
            username=username,
            joined_at=datetime.utcnow()
        )
        room.users.append(room_user)
        room.last_activity = datetime.utcnow()
        
        # Actualizar mapeo
        self.user_to_room[user_id] = code
        
        logger.info(f"Usuario {username} ({user_id}) se unió a sala {code}")
        return True
    
    def remove_user_from_room(self, code: str, user_id: int) -> bool:
        """
        Remueve un usuario de una sala específica.
        
        Returns:
            bool: True si se removió exitosamente
        """
        room = self.get_room(code)
        if not room:
            return False
        
        # Remover usuario de la lista
        room.users = [u for u in room.users if u.user_id != user_id]
        room.last_activity = datetime.utcnow()
        
        # Actualizar mapeo
        if user_id in self.user_to_room and self.user_to_room[user_id] == code:
            del self.user_to_room[user_id]
        
        logger.info(f"Usuario {user_id} salió de sala {code}")
        return True
    
    def remove_user_from_current_room(self, user_id: int) -> Optional[str]:
        """
        Remueve un usuario de su sala actual (si está en alguna).
        
        Returns:
            Optional[str]: Código de la sala de la que salió, o None
        """
        if user_id not in self.user_to_room:
            return None
        
        current_room_code = self.user_to_room[user_id]
        self.remove_user_from_room(current_room_code, user_id)
        return current_room_code
    
    def get_user_current_room(self, user_id: int) -> Optional[str]:
        """Obtiene el código de la sala actual del usuario"""
        return self.user_to_room.get(user_id)
    
    def delete_room(self, code: str) -> bool:
        """Elimina una sala"""
        if code not in self.rooms:
            return False
        
        # Remover todos los usuarios del mapeo
        room = self.rooms[code]
        for user in room.users:
            if user.user_id in self.user_to_room:
                del self.user_to_room[user.user_id]
        
        # Eliminar sala
        del self.rooms[code]
        logger.info(f"Sala eliminada: {code}")
        return True
    
    async def cleanup_empty_rooms(self):
        """
        Tarea de limpieza que elimina salas vacías después del timeout configurado.
        Se ejecuta periódicamente en background.
        """
        while True:
            try:
                await asyncio.sleep(settings.room_cleanup_interval_seconds)
                
                now = datetime.utcnow()
                timeout = timedelta(seconds=settings.room_empty_timeout_seconds)
                rooms_to_delete = []
                
                for code, room in self.rooms.items():
                    # Si la sala está vacía y ha pasado el timeout
                    if len(room.users) == 0:
                        time_since_activity = now - room.last_activity
                        if time_since_activity > timeout:
                            rooms_to_delete.append(code)
                
                # Eliminar salas
                for code in rooms_to_delete:
                    self.delete_room(code)
                    logger.info(f"Sala {code} eliminada por inactividad")
                
                if rooms_to_delete:
                    logger.info(f"Limpieza completada: {len(rooms_to_delete)} salas eliminadas")
                    
            except Exception as e:
                logger.error(f"Error en limpieza de salas: {e}")
    
    def start_cleanup_task(self):
        """Inicia la tarea de limpieza en background"""
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self.cleanup_empty_rooms())
            logger.info("Tarea de limpieza de salas iniciada")
    
    def stop_cleanup_task(self):
        """Detiene la tarea de limpieza"""
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()
            logger.info("Tarea de limpieza de salas detenida")
    
    def get_stats(self) -> dict:
        """Obtiene estadísticas del gestor de salas"""
        total_users = sum(len(room.users) for room in self.rooms.values())
        return {
            "total_rooms": len(self.rooms),
            "total_users": total_users,
            "empty_rooms": sum(1 for room in self.rooms.values() if len(room.users) == 0)
        }


# Instancia global del gestor de salas
room_manager = RoomManager()
