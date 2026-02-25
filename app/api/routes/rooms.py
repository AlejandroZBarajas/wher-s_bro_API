from fastapi import APIRouter, HTTPException, status, Query
from app.models.room import (
    CreateRoomResponse,
    JoinRoomRequest,
    JoinRoomResponse,
    LeaveRoomResponse,
    Room
)
from app.services.room_service import room_service
from app.core.room_manager import room_manager
from typing import Optional

router = APIRouter(prefix="/rooms", tags=["rooms"])


@router.post("/create", response_model=CreateRoomResponse, status_code=status.HTTP_201_CREATED)
async def create_room():
    """
    Crea una nueva sala con un código único de 6 caracteres alfanuméricos.
    
    El código se genera usando milisegundos del sistema como seed.
    La sala permanecerá activa hasta 2 minutos después de quedar vacía.
    
    Returns:
        CreateRoomResponse: Información de la sala creada incluyendo el código
    """
    try:
        response = room_service.create_room()
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear la sala: {str(e)}"
        )


@router.post("/{code}/join", response_model=JoinRoomResponse)
async def join_room(code: str, request: JoinRoomRequest):
    """
    Une un usuario a una sala existente mediante su código.
    
    Si el usuario ya está en otra sala, será removido de ella automáticamente.
    Un usuario solo puede estar en una sala a la vez.
    
    Args:
        code: Código de 6 caracteres de la sala
        request: Datos del usuario (user_id, username)
    
    Returns:
        JoinRoomResponse: Confirmación y lista de usuarios en la sala
    """
    code = code.upper()  # Normalizar código a mayúsculas
    
    success, response = room_service.join_room(
        code=code,
        user_id=request.user_id,
        username=request.username
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=response.message
        )
    
    return response


@router.post("/leave", response_model=LeaveRoomResponse)
async def leave_room(user_id: int = Query(..., description="ID del usuario que sale de la sala")):
    """
    Remueve un usuario de su sala actual.
    
    Args:
        user_id: ID del usuario
    
    Returns:
        LeaveRoomResponse: Confirmación de salida
    """
    success, response = room_service.leave_room(user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=response.message
        )
    
    return response


@router.get("/{code}", response_model=Room)
async def get_room_info(code: str):
    """
    Obtiene información detallada de una sala.
    
    Args:
        code: Código de la sala
    
    Returns:
        Room: Información completa de la sala incluyendo usuarios activos
    """
    code = code.upper()
    room = room_service.get_room_info(code)
    
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La sala no existe o ha expirado"
        )
    
    return room


@router.get("/user/{user_id}/current", response_model=Optional[Room])
async def get_user_current_room(user_id: int):
    """
    Obtiene la sala actual en la que está un usuario.
    
    Args:
        user_id: ID del usuario
    
    Returns:
        Room: Sala actual del usuario o None si no está en ninguna
    """
    room = room_service.get_user_room(user_id)
    
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El usuario no está en ninguna sala"
        )
    
    return room


@router.get("/stats", response_model=dict)
async def get_stats():
    """
    Obtiene estadísticas del sistema de salas.
    
    Útil para monitoreo y debugging.
    
    Returns:
        dict: Estadísticas (total de salas, usuarios, salas vacías)
    """
    return room_manager.get_stats()
