# Location Sharing API

API REST para compartir ubicación en tiempo real entre usuarios organizados en salas.

## Características

- ✅ Crear salas con códigos únicos de 6 caracteres
- ✅ Unirse a salas existentes
- ✅ Salir de salas
- ✅ Gestión automática de salas (limpieza después de 2 minutos de inactividad)
- ✅ Un usuario solo puede estar en una sala a la vez
- 🔄 WebSocket para ubicaciones en tiempo real (pendiente - otro miembro del equipo)
- 🔄 Autenticación de usuarios (pendiente - integración con sistema externo)
- 🔄 Conexión a base de datos (pendiente - configuración externa)

## Estructura del Proyecto

```
project/
├── app/
│   ├── main.py                 # Aplicación FastAPI principal
│   ├── api/
│   │   └── routes/
│   │       ├── rooms.py        # Endpoints de salas
│   │       └── auth.py         # [PENDIENTE] Autenticación
│   ├── models/
│   │   ├── room.py            # Modelos de salas
│   │   └── user.py            # Modelos de usuario
│   ├── services/
│   │   ├── room_service.py    # Lógica de negocio de salas
│   │   └── code_generator.py # Generador de códigos
│   ├── core/
│   │   ├── config.py          # Configuración
│   │   └── room_manager.py    # Gestor de salas en memoria
│   └── database/
│       ├── connection.py       # [PENDIENTE] Conexión a BD
│       └── session.py          # [PENDIENTE] Sesiones de BD
├── requirements.txt
└── .env
```

## Instalación

1. Instalar dependencias:
```bash
pip install -r requirements.txt
```

2. Configurar variables de entorno (editar `.env` si es necesario):
```bash
# Ya viene configurado con valores por defecto
```

## Ejecutar

```bash
# Opción 1: Usando uvicorn directamente
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Opción 2: Ejecutando el archivo main.py
python -m app.main
```

La API estará disponible en: `http://localhost:8000`

## Documentación Interactiva

FastAPI genera documentación automática:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Endpoints Disponibles

### Health Check

**GET** `/`
- Verifica que la API está funcionando

**GET** `/health`
- Información de salud y estadísticas del sistema

### Salas (Rooms)

**POST** `/rooms/create`
- Crea una nueva sala
- Retorna: código de sala de 6 caracteres

**POST** `/rooms/{code}/join`
- Une un usuario a una sala existente
- Body: `{"user_id": int, "username": string}`
- Retorna: confirmación y lista de usuarios en la sala

**POST** `/rooms/leave`
- Remueve un usuario de su sala actual
- Query param: `user_id`
- Retorna: confirmación de salida

**GET** `/rooms/{code}`
- Obtiene información de una sala específica
- Retorna: detalles de la sala y usuarios activos

**GET** `/rooms/user/{user_id}/current`
- Obtiene la sala actual de un usuario
- Retorna: información de la sala o 404

**GET** `/rooms/stats`
- Estadísticas del sistema de salas
- Retorna: total de salas, usuarios, salas vacías

### Autenticación (Pendiente)

**POST** `/auth/register` - [501 Not Implemented]

**POST** `/auth/login` - [501 Not Implemented]

**POST** `/auth/logout` - [501 Not Implemented]

## Ejemplos de Uso

### Crear una sala

```bash
curl -X POST http://localhost:8000/rooms/create
```

Respuesta:
```json
{
  "code": "A3B7K9",
  "created_at": "2024-02-24T10:30:00",
  "message": "Sala creada exitosamente"
}
```

### Unirse a una sala

```bash
curl -X POST http://localhost:8000/rooms/A3B7K9/join \
  -H "Content-Type: application/json" \
  -d '{"user_id": 123, "username": "JohnDoe"}'
```

Respuesta:
```json
{
  "code": "A3B7K9",
  "message": "Te has unido a la sala A3B7K9",
  "users_in_room": ["JohnDoe"]
}
```

### Salir de una sala

```bash
curl -X POST "http://localhost:8000/rooms/leave?user_id=123"
```

Respuesta:
```json
{
  "message": "Has salido de la sala A3B7K9",
  "code": "A3B7K9"
}
```

### Ver información de una sala

```bash
curl http://localhost:8000/rooms/A3B7K9
```

### Ver estadísticas

```bash
curl http://localhost:8000/rooms/stats
```

## Configuración

Editar `.env` para cambiar configuraciones:

```env
# Longitud del código de sala (default: 6)
ROOM_CODE_LENGTH=6

# Intervalo de limpieza en segundos (default: 60)
ROOM_CLEANUP_INTERVAL_SECONDS=60

# Timeout de salas vacías en segundos (default: 120 = 2 minutos)
ROOM_EMPTY_TIMEOUT_SECONDS=120
```

## Características Técnicas

### Generación de Códigos
- Códigos alfanuméricos de 6 caracteres (A-Z, 0-9)
- Excluye caracteres confusos (O, I) para evitar confusión con 0 y 1
- Usa milisegundos del sistema como seed para el algoritmo
- Verifica unicidad antes de crear la sala

### Gestión de Salas
- Las salas se mantienen en memoria (no persisten)
- Limpieza automática cada 60 segundos
- Salas vacías se eliminan después de 2 minutos
- Un usuario solo puede estar en una sala a la vez

### Restricciones
- Un usuario puede estar en máximo 1 sala simultáneamente
- Al unirse a una nueva sala, el usuario sale automáticamente de la anterior
- Las salas no tienen límite de usuarios (diseñado para 8 personas)
- No hay roles de administrador en las salas

## Pendientes de Implementación

1. **WebSocket para ubicaciones** (otro miembro del equipo)
   - Conexión WebSocket para envío/recepción de ubicaciones
   - Broadcast de coordenadas a todos los usuarios de la sala

2. **Autenticación** (integración con sistema externo)
   - Endpoints de registro y login
   - Generación de JWT tokens
   - Middleware de autenticación

3. **Base de Datos** (configuración externa)
   - Conexión a BD para persistir usuarios
   - Migración de datos
   - Session management

## Testing

Para probar la API rápidamente, usa la documentación interactiva en:
http://localhost:8000/docs

## Notas para el Equipo

- Los archivos marcados con `[PENDIENTE]` contienen comentarios explicativos sobre lo que falta implementar
- La estructura está lista para agregar el WebSocket sin modificar la lógica REST existente
- La autenticación se puede integrar como middleware sin afectar los endpoints actuales
- Las salas se pueden migrar a BD cuando esté lista la conexión
