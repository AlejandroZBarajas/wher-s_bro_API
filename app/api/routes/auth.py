from fastapi import APIRouter, HTTPException, status
from app.models.user import LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def register():
    """
    [PENDIENTE] Endpoint de registro.
    Será implementado cuando se integre el sistema de autenticación externo.
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Endpoint pendiente de implementación. Será integrado con el sistema de auth externo."
    )


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def login(request: LoginRequest):
    """
    [PENDIENTE] Endpoint de login.
    Será implementado cuando se integre el sistema de autenticación externo.
    
    Expected behavior:
    - Validar credenciales del usuario
    - Generar JWT token
    - Retornar TokenResponse con access_token, user_id y username
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Endpoint pendiente de implementación. Será integrado con el sistema de auth externo."
    )


@router.post("/logout", status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def logout():
    """
    [PENDIENTE] Endpoint de logout.
    Será implementado cuando se integre el sistema de autenticación externo.
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Endpoint pendiente de implementación. Será integrado con el sistema de auth externo."
    )