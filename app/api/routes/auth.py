from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import Session, select
from datetime import timedelta
from app.models.user import User, LoginRequest, TokenResponse
from app.database.session import get_session
from app.services.auth_service import (
    authenticate_user,
    create_access_token,
    get_password_hash,
    get_current_user
)
from app.core.config import settings
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/auth", tags=["authentication"])


class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest, session: Session = Depends(get_session)):
    """
    Registra un nuevo usuario.
    
    Args:
        request: Datos del nuevo usuario (username, email, password)
    
    Returns:
        TokenResponse: Token de acceso JWT, user_id y username
    """
    # Verificar si el email ya existe
    statement = select(User).where(User.email == request.email)
    existing_user = session.exec(statement).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado"
        )
    
    # Verificar si el username ya existe
    statement = select(User).where(User.username == request.username)
    existing_user = session.exec(statement).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El username ya está en uso"
        )
    
    # Crear nuevo usuario
    hashed_password = get_password_hash(request.password)
    new_user = User(
        username=request.username,
        email=request.email,
        hashed_password=hashed_password
    )
    
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    
    # Crear token de acceso
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": new_user.id, "username": new_user.username},
        expires_delta=access_token_expires
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=new_user.id,
        username=new_user.username
    )


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, session: Session = Depends(get_session)):
    """
    Autentica un usuario y retorna un JWT token.
    
    Args:
        request: Credenciales del usuario (email, password)
    
    Returns:
        TokenResponse: Token de acceso JWT, user_id y username
    """
    user = authenticate_user(request.email, request.password, session)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Crear token de acceso
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.id, "username": user.username},
        expires_delta=access_token_expires
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=user.id,
        username=user.username
    )


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """
    Cierra la sesión del usuario.
    
    Nota: En JWT stateless, el logout se maneja en el cliente eliminando el token.
    Este endpoint existe para futuras implementaciones (ej: blacklist de tokens).
    """
    return {"message": f"Sesión cerrada para {current_user.username}"}


@router.get("/me", response_model=dict)
async def get_me(current_user: User = Depends(get_current_user)):
    """
    Obtiene información del usuario autenticado actual.
    
    Requiere: Header Authorization: Bearer <token>
    """
    return {
        "user_id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "created_at": current_user.created_at
    }
