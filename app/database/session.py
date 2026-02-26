"""
Módulo de gestión de sesiones de base de datos.
"""

from sqlmodel import Session
from app.database.connection import get_engine
from typing import Generator


def get_session() -> Generator[Session, None, None]:
    """
    Dependency para obtener una sesión de base de datos.
    
    Uso en endpoints:
        @router.get("/users/{user_id}")
        async def get_user(user_id: int, session: Session = Depends(get_session)):
            user = session.get(User, user_id)
            return user
    """
    engine = get_engine()
    if not engine:
        raise Exception("Base de datos no inicializada")
    
    with Session(engine) as session:
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
