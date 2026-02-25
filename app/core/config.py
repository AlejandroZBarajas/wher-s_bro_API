from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    app_name: str = "Location Sharing API"
    debug: bool = True
    
    # Configuración de base de datos
    # [PENDIENTE] Descomentar y configurar cuando se integre la BD externa
    # database_url: Optional[str] = None
    
    # Configuración de salas
    room_code_length: int = 6
    room_cleanup_interval_seconds: int = 60  # Revisar salas cada 60 segundos
    room_empty_timeout_seconds: int = 120  # 2 minutos de timeout
    
    class Config:
        env_file = ".env"


settings = Settings()
