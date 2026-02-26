from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.core.config import settings
from app.core.room_manager import room_manager
from app.api.routes import rooms, auth, websockets

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestión del ciclo de vida de la aplicación.
    Se ejecuta al iniciar y al cerrar la aplicación.
    """
    # Startup
    logger.info("Iniciando aplicación...")
    
    # Iniciar tarea de limpieza de salas
    room_manager.start_cleanup_task()
    logger.info("Tarea de limpieza de salas iniciada")
    
    # [PENDIENTE] Aquí se inicializaría la conexión a la base de datos
    # from app.database.connection import engine
    # SQLModel.metadata.create_all(engine)
    
    yield
    
    # Shutdown
    logger.info("Cerrando aplicación...")
    room_manager.stop_cleanup_task()
    logger.info("Tarea de limpieza de salas detenida")


# Crear aplicación FastAPI
app = FastAPI(
    title=settings.app_name,
    description="API para compartir ubicación en tiempo real entre usuarios en salas",
    version="1.0.0",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar routers
app.include_router(rooms.router)
app.include_router(auth.router)
app.include_router(websockets.router)

@app.get("/", tags=["health"])
async def root():
    """Endpoint raíz para verificar que la API está funcionando"""
    return {
        "message": "Location Sharing API",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint"""
    stats = room_manager.get_stats()
    return {
        "status": "healthy",
        "rooms": stats
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
