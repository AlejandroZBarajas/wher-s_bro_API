"""
[PENDIENTE] Módulo de conexión a la base de datos.

Este módulo manejará la conexión a la base de datos externa cuando esté lista.
Debe configurarse con las credenciales apropiadas en el archivo .env

Ejemplo de uso esperado:
    from sqlmodel import create_engine
    from app.core.config import settings
    
    engine = create_engine(settings.database_url)
    
Para SQLModel, típicamente se usa:
    - create_engine() para crear el motor de BD
    - Session para manejar transacciones
    - SQLModel.metadata.create_all(engine) para crear tablas
"""

# TODO: Implementar cuando se tenga la URL de la base de datos
# TODO: Configurar pool de conexiones
# TODO: Implementar health check de la BD
