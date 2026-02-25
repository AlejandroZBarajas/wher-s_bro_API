import time
import random
import string
from app.core.config import settings


class CodeGenerator:
    """
    Generador de códigos únicos de sala usando milisegundos del sistema.
    """
    
    @staticmethod
    def generate_room_code() -> str:
        """
        Genera un código alfanumérico de 6 caracteres.
        Usa milisegundos del sistema como seed para el algoritmo.
        
        Returns:
            str: Código de 6 caracteres (números y letras mayúsculas)
        """
        # Obtener milisegundos actuales como seed
        milliseconds = int(time.time() * 1000)
        
        # Usar milisegundos como seed para random
        random.seed(milliseconds)
        
        # Caracteres permitidos: A-Z y 0-9 (excluyendo letras confusas como O, I)
        # Para evitar confusión entre 0/O y 1/I
        characters = string.ascii_uppercase.replace('O', '').replace('I', '') + string.digits
        
        # Generar código de longitud configurada
        code = ''.join(random.choices(characters, k=settings.room_code_length))
        
        return code
    
    @staticmethod
    def is_valid_code(code: str) -> bool:
        """
        Valida si un código tiene el formato correcto.
        
        Args:
            code: Código a validar
            
        Returns:
            bool: True si el código es válido
        """
        if not code or len(code) != settings.room_code_length:
            return False
        
        # Verificar que solo contenga caracteres alfanuméricos
        return code.isalnum() and code.isupper()


# Instancia global del generador
code_generator = CodeGenerator()
