"""
Módulo de conexión a la base de datos MySQL.
"""

from sqlmodel import create_engine, SQLModel
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Crear engine de SQLModel
engine = None

def init_db():
    """
    Inicializa la conexión a la base de datos MySQL y crea las tablas.
    Se llama desde app.main.py en el startup event.
    """
    global engine
    
    if not settings.database_url:
        logger.warning("DATABASE_URL no configurada. La BD no estará disponible.")
        return None
    
    try:
        # Configuración específica para MySQL
        engine = create_engine(
            settings.database_url,
            echo=settings.debug,  # Log SQL queries en modo debug
            pool_pre_ping=True,  # Verificar conexión antes de usar
            pool_size=10,  # Número de conexiones en el pool
            max_overflow=20,  # Conexiones adicionales permitidas
            pool_recycle=3600,  # Reciclar conexiones cada hora (importante para MySQL)
        )
        
        # Crear todas las tablas definidas en los modelos
        # Nota: init.sql ya crea la tabla, pero esto no hace daño
        SQLModel.metadata.create_all(engine)
        
        logger.info("✅ Base de datos MySQL conectada exitosamente")
        return engine
        
    except Exception as e:
        logger.error(f"❌ Error al conectar con MySQL: {e}")
        raise


def get_engine():
    """Retorna el engine de la base de datos"""
    return engine


def close_db():
    """Cierra la conexión a la base de datos"""
    global engine
    if engine:
        engine.dispose()
        logger.info("Base de datos MySQL desconectada")
