from typing import Optional, Tuple
from app.models.room import Room, CreateRoomResponse, JoinRoomResponse, LeaveRoomResponse
from app.core.room_manager import room_manager
from app.services.code_generator import code_generator
from datetime import datetime


class RoomService:
    """Servicio que contiene la lógica de negocio de las salas"""
    
    @staticmethod
    def create_room() -> CreateRoomResponse:
        """
        Crea una nueva sala con un código único.
        
        Returns:
            CreateRoomResponse: Información de la sala creada
        """
        # Generar código único
        max_attempts = 10
        code = None
        
        for _ in range(max_attempts):
            candidate_code = code_generator.generate_room_code()
            if not room_manager.room_exists(candidate_code):
                code = candidate_code
                break
        
        if not code:
            raise Exception("No se pudo generar un código único después de varios intentos")
        
        # Crear sala
        room = room_manager.create_room(code)
        
        return CreateRoomResponse(
            code=room.code,
            created_at=room.created_at,
            message="Sala creada exitosamente"
        )
    
    @staticmethod
    def join_room(code: str, user_id: int, username: str) -> Tuple[bool, JoinRoomResponse]:
        """
        Une un usuario a una sala existente.
        
        Args:
            code: Código de la sala
            user_id: ID del usuario
            username: Nombre del usuario
            
        Returns:
            Tuple[bool, JoinRoomResponse]: (éxito, respuesta)
        """
        # Validar código
        if not code_generator.is_valid_code(code):
            return False, JoinRoomResponse(
                code=code,
                message="Código de sala inválido",
                users_in_room=[]
            )
        
        # Verificar que la sala existe
        room = room_manager.get_room(code)
        if not room:
            return False, JoinRoomResponse(
                code=code,
                message="La sala no existe o ha expirado",
                users_in_room=[]
            )
        
        # Agregar usuario a la sala
        success = room_manager.add_user_to_room(code, user_id, username)
        
        if not success:
            return False, JoinRoomResponse(
                code=code,
                message="No se pudo unir a la sala",
                users_in_room=[]
            )
        
        # Obtener lista actualizada de usuarios
        room = room_manager.get_room(code)
        usernames = [u.username for u in room.users]
        
        return True, JoinRoomResponse(
            code=code,
            message=f"Te has unido a la sala {code}",
            users_in_room=usernames
        )
    
    @staticmethod
    def leave_room(user_id: int) -> Tuple[bool, LeaveRoomResponse]:
        """
        Remueve un usuario de su sala actual.
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Tuple[bool, LeaveRoomResponse]: (éxito, respuesta)
        """
        # Obtener sala actual del usuario
        current_room = room_manager.get_user_current_room(user_id)
        
        if not current_room:
            return False, LeaveRoomResponse(
                message="No estás en ninguna sala"
            )
        
        # Remover usuario de la sala
        success = room_manager.remove_user_from_room(current_room, user_id)
        
        if success:
            return True, LeaveRoomResponse(
                message=f"Has salido de la sala {current_room}",
                code=current_room
            )
        else:
            return False, LeaveRoomResponse(
                message="Error al salir de la sala"
            )
    
    @staticmethod
    def get_room_info(code: str) -> Optional[Room]:
        """
        Obtiene información de una sala.
        
        Args:
            code: Código de la sala
            
        Returns:
            Optional[Room]: Información de la sala o None si no existe
        """
        return room_manager.get_room(code)
    
    @staticmethod
    def get_user_room(user_id: int) -> Optional[Room]:
        """
        Obtiene la sala actual de un usuario.
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Optional[Room]: Sala actual o None
        """
        room_code = room_manager.get_user_current_room(user_id)
        if room_code:
            return room_manager.get_room(room_code)
        return None


# Instancia global del servicio
room_service = RoomService()
