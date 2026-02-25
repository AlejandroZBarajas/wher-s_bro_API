from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class User(SQLModel, table=True):
    """
    Modelo de usuario para autenticación.
    [PENDIENTE] Este modelo será gestionado por el sistema de autenticación externo.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class LoginRequest(SQLModel):
    """Request body para login"""
    email: str
    password: str


class TokenResponse(SQLModel):
    """Response body para autenticación exitosa"""
    access_token: str
    token_type: str = "bearer"
    user_id: int
    username: str
