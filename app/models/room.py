from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class RoomUser(BaseModel):
    """Usuario activo en una sala"""
    user_id: int
    username: str
    joined_at: datetime


class Room(BaseModel):
    """
    Modelo de sala en memoria.
    No se persiste en base de datos por ahora.
    """
    code: str
    created_at: datetime
    last_activity: datetime
    users: List[RoomUser] = []
    
    class Config:
        from_attributes = True


class CreateRoomResponse(BaseModel):
    """Response al crear una sala"""
    code: str
    created_at: datetime
    message: str = "Sala creada exitosamente"


class JoinRoomRequest(BaseModel):
    """Request para unirse a una sala"""
    user_id: int
    username: str


class JoinRoomResponse(BaseModel):
    """Response al unirse a una sala"""
    code: str
    message: str
    users_in_room: List[str]  # Lista de usernames


class LeaveRoomResponse(BaseModel):
    """Response al salir de una sala"""
    message: str
    code: Optional[str] = None
