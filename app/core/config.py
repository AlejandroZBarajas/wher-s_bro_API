from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    app_name: str = "Location Sharing API"
    debug: bool = False
    
    # Configuración de base de datos
    database_url: Optional[str] = None
    db_password: Optional[str] = None
    db_root_password: Optional[str] = None
    
    # Configuración de CORS (como string, lo parseamos después)
    allowed_origins: str = "*"
    
    # Configuración de salas
    room_code_length: int = 6
    room_cleanup_interval_seconds: int = 60
    room_empty_timeout_seconds: int = 120
    
    # Configuración de JWT
    secret_key: str = "your-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    class Config:
        env_file = ".env"
        extra = "allow"
    
    def get_allowed_origins(self):
        """Convierte la string de CORS a lista"""
        if self.allowed_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.allowed_origins.split(",")]


settings = Settings()
