# 🚀 Guía Completa de Deployment - API con WebSocket + MySQL + Nginx

## 📋 Arquitectura

```
┌─────────────────────────────────────────────────────┐
│                    Internet                          │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
          ┌──────────────────────┐
          │   Nginx (Puerto 80)   │
          │  - Proxy Reverso      │
          │  - Load Balancer      │
          │  - SSL Termination    │
          └──────────┬───────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
         ▼                       ▼
┌────────────────┐      ┌──────────────────┐
│  FastAPI API   │      │    WebSocket     │
│  (Puerto 8000) │      │  /ws/{code}/{u}  │
│  - REST API    │      │  - Ubicaciones   │
│  - Auth JWT    │      │  - Tiempo Real   │
└────────┬───────┘      └──────────────────┘
         │
         ▼
┌────────────────────┐
│  MySQL (Puerto 3306)│
│  - Usuarios        │
│  - Autenticación   │
└────────────────────┘
```

---

## 🔧 Paso 1: Preparar EC2

```bash
# Conectar a tu instancia
ssh -i tu-key.pem ubuntu@tu-ip-elastica

# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Cerrar sesión y volver a conectar
exit
ssh -i tu-key.pem ubuntu@tu-ip-elastica

# Verificar
docker --version
docker-compose --version
```

---

## 📦 Paso 2: Subir el Proyecto

### Opción A: Con Git (Recomendado)

```bash
cd ~
git clone tu-repositorio.git location-api
cd location-api
```

### Opción B: Con SCP (desde tu máquina local)

```bash
# En tu máquina local:
scp -i tu-key.pem -r /ruta/proyecto/* ubuntu@tu-ip-elastica:~/location-api/
```

---

## 🔐 Paso 3: Configurar Variables de Entorno

```bash
cd ~/location-api

# Generar SECRET_KEY seguro
python3 generate_secret.py

# Crear archivo .env
nano .env
```

**Contenido del `.env`:**

```env
# Base de datos MySQL
DB_ROOT_PASSWORD=super_secure_root_password_123
DB_PASSWORD=secure_user_password_456

# JWT Secret (usar el generado por generate_secret.py)
SECRET_KEY=pegaaquilaclavegeneradaporelscript

# Configuración
DEBUG=False
ROOM_CODE_LENGTH=6
ROOM_CLEANUP_INTERVAL_SECONDS=60
ROOM_EMPTY_TIMEOUT_SECONDS=120
```

**⚠️ IMPORTANTE:** 
- Cambia las contraseñas a valores seguros
- Usa el SECRET_KEY generado por `generate_secret.py`
- NO compartas este archivo (ya está en .gitignore)

---

## 📁 Paso 4: Estructura de Archivos

Asegúrate de tener estos archivos en tu proyecto:

```
location-api/
├── Dockerfile
├── docker-compose.yml
├── init_mysql.sql
├── nginx.conf
├── requirements.txt
├── .env
├── generate_secret.py
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── api/
│   │   └── routes/
│   │       ├── rooms.py
│   │       ├── auth.py
│   │       └── websocket.py  ← Tu compañero agregó esto
│   ├── models/
│   ├── services/
│   ├── core/
│   └── database/
│       ├── connection.py
│       └── session.py
└── ssl/  (crear vacío por ahora)
```

---

## 🏗️ Paso 5: Crear Directorios Necesarios

```bash
cd ~/location-api

# Crear directorios
mkdir -p logs logs/nginx ssl

# Permisos
chmod 755 logs logs/nginx ssl
```

---

## 🚀 Paso 6: Construir y Ejecutar

```bash
# Construir imágenes
docker-compose build

# Iniciar servicios
docker-compose up -d

# Ver logs en tiempo real
docker-compose logs -f

# Ver estado de contenedores
docker-compose ps
```

**Salida esperada:**

```
NAME              IMAGE               STATUS       PORTS
location-api      location-api        Up           0.0.0.0:8000->8000/tcp
location-db       mysql:8.0           Up (healthy) 0.0.0.0:3306->3306/tcp
location-nginx    nginx:alpine        Up           0.0.0.0:80->80/tcp
```

---

## ✅ Paso 7: Verificar que Funciona

### 7.1 Health Check

```bash
# Desde el servidor
curl http://localhost/health

# Desde fuera
curl http://tu-ip-elastica/health
```

**Respuesta esperada:**
```json
{
  "status": "healthy",
  "rooms": {
    "total_rooms": 0,
    "total_users": 0,
    "empty_rooms": 0
  }
}
```

### 7.2 Ver Documentación

Abre en tu navegador:
```
http://tu-ip-elastica/docs
```

### 7.3 Verificar Base de Datos

```bash
# Conectar a MySQL
docker-compose exec db mysql -u location_user -p location_db

# Cuando pida password, usa el DB_PASSWORD de tu .env

# Una vez dentro:
SHOW TABLES;
SELECT * FROM user;
exit
```

---

## 🧪 Paso 8: Probar la API

### 8.1 Registrar Usuario

```bash
curl -X POST http://tu-ip-elastica/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alejandro",
    "email": "alejandro@test.com",
    "password": "mipassword123"
  }'
```

**Respuesta esperada:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user_id": 2,
  "username": "alejandro"
}
```

**⚠️ Guarda el `access_token` para usarlo después**

### 8.2 Login

```bash
curl -X POST http://tu-ip-elastica/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alejandro@test.com",
    "password": "mipassword123"
  }'
```

### 8.3 Ver Mi Perfil (con Auth)

```bash
# Reemplaza TU_TOKEN con el access_token recibido
TOKEN="eyJ0eXAiOiJKV1QiLCJhbGc..."

curl http://tu-ip-elastica/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

### 8.4 Crear Sala

```bash
curl -X POST http://tu-ip-elastica/rooms/create
```

**Respuesta:**
```json
{
  "code": "A3B7K9",
  "created_at": "2024-02-24T10:30:00",
  "message": "Sala creada exitosamente"
}
```

### 8.5 Unirse a Sala

```bash
curl -X POST http://tu-ip-elastica/rooms/A3B7K9/join \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 2,
    "username": "alejandro"
  }'
```

---

## 🌐 Paso 9: Probar WebSocket

### Desde JavaScript (navegador o Node.js)

```javascript
// URL del WebSocket
const ws = new WebSocket('ws://tu-ip-elastica/ws/A3B7K9/alejandro');

// Cuando se conecta
ws.onopen = () => {
    console.log('Conectado!');
    
    // Enviar ubicación
    ws.send(JSON.stringify({
        event: "UPDATE_LOCATION",
        data: {
            lat: 16.7569,
            lon: -93.1292
        }
    }));
};

// Recibir actualizaciones
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Mensaje recibido:', data);
    
    if (data.event === "FRIEND_MOVED") {
        console.log(`${data.data.username} movió a: ${data.data.lat}, ${data.data.lon}`);
    }
};

// Errores
ws.onerror = (error) => {
    console.error('WebSocket error:', error);
};

// Desconexión
ws.onclose = () => {
    console.log('Desconectado');
};
```

### Desde Python (para pruebas)

```bash
pip install websockets

python3 << 'EOF'
import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://tu-ip-elastica/ws/A3B7K9/testuser"
    
    async with websockets.connect(uri) as websocket:
        # Enviar ubicación
        await websocket.send(json.dumps({
            "event": "UPDATE_LOCATION",
            "data": {"lat": 16.7569, "lon": -93.1292}
        }))
        
        # Recibir respuestas
        while True:
            response = await websocket.recv()
            print(f"Recibido: {response}")

asyncio.run(test_websocket())
EOF
```

---

## 🔒 Paso 10: Configurar HTTPS

### Opción 1: Con Dominio (Let's Encrypt) - RECOMENDADO

```bash
# 1. Detener nginx temporalmente
docker-compose stop nginx

# 2. Instalar certbot
sudo apt install certbot

# 3. Obtener certificado
sudo certbot certonly --standalone -d tu-dominio.com

# 4. Copiar certificados
sudo cp /etc/letsencrypt/live/tu-dominio.com/fullchain.pem ~/location-api/ssl/
sudo cp /etc/letsencrypt/live/tu-dominio.com/privkey.pem ~/location-api/ssl/
sudo chown $USER:$USER ~/location-api/ssl/*

# 5. Editar nginx.conf
cd ~/location-api
nano nginx.conf

# Buscar la sección "SERVIDOR HTTPS" y:
# - Descomentarla (quitar los #)
# - Cambiar "tu-dominio.com" por tu dominio real

# 6. Reiniciar nginx
docker-compose start nginx

# 7. Verificar HTTPS
curl https://tu-dominio.com/health
```

**Ahora tu WebSocket será:**
```
wss://tu-dominio.com/ws/{room_code}/{username}
```

### Opción 2: Sin Dominio (Certificado Autofirmado)

```bash
# Generar certificado
cd ~/location-api
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/privkey.pem \
  -out ssl/fullchain.pem \
  -subj "/C=MX/ST=Chiapas/L=Tuxtla/O=MyApp/CN=tu-ip-elastica"

# Editar nginx.conf y descomentar sección HTTPS
nano nginx.conf

# Reiniciar
docker-compose restart nginx
```

**⚠️ Nota:** Los navegadores darán advertencia de seguridad con certificado autofirmado.

---

## 🔧 Comandos Útiles

### Ver Logs

```bash
# Todos los logs
docker-compose logs -f

# Solo API
docker-compose logs -f api

# Solo Base de Datos
docker-compose logs -f db

# Solo Nginx
docker-compose logs -f nginx
```

### Reiniciar Servicios

```bash
# Reiniciar todo
docker-compose restart

# Reiniciar solo la API
docker-compose restart api

# Detener todo
docker-compose stop

# Iniciar servicios detenidos
docker-compose start
```

### Acceder a Contenedores

```bash
# Shell en el contenedor de la API
docker-compose exec api bash

# MySQL CLI
docker-compose exec db mysql -u location_user -p location_db

# Ver variables de entorno de la API
docker-compose exec api env
```

### Backups de Base de Datos

```bash
# Crear backup
docker-compose exec db mysqldump -u location_user -p location_db > backup_$(date +%Y%m%d).sql

# Restaurar backup
docker-compose exec -T db mysql -u location_user -p location_db < backup_20240224.sql
```

### Limpiar y Reiniciar

```bash
# ⚠️ CUIDADO: Esto borra todos los datos
docker-compose down -v
docker system prune -a -f
docker-compose up -d --build
```

---

## 📱 Integración con Android

### URL Base

```kotlin
const val BASE_URL = "http://tu-ip-elastica"  // o https://tu-dominio.com
```

### 1. Registrar Usuario

```kotlin
// POST /auth/register
val response = api.register(RegisterRequest(
    username = "alejandro",
    email = "alejandro@test.com",
    password = "mipassword"
))

// Guardar token
sharedPreferences.edit()
    .putString("access_token", response.access_token)
    .putInt("user_id", response.user_id)
    .putString("username", response.username)
    .apply()
```

### 2. Login

```kotlin
// POST /auth/login
val response = api.login(LoginRequest(
    email = "alejandro@test.com",
    password = "mipassword"
))

// Guardar token
saveToken(response.access_token)
```

### 3. Crear/Unirse a Sala

```kotlin
// POST /rooms/create
val room = api.createRoom()
val roomCode = room.code  // "A3B7K9"

// POST /rooms/{code}/join
api.joinRoom(roomCode, JoinRequest(
    user_id = userId,
    username = username
))
```

### 4. Conectar WebSocket

```kotlin
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.WebSocket
import okhttp3.WebSocketListener

val client = OkHttpClient()

val request = Request.Builder()
    .url("ws://tu-ip-elastica/ws/$roomCode/$username")
    .build()

val webSocket = client.newWebSocket(request, object : WebSocketListener() {
    override fun onOpen(webSocket: WebSocket, response: Response) {
        println("WebSocket conectado")
    }
    
    override fun onMessage(webSocket: WebSocket, text: String) {
        val data = Json.decodeFromString<WebSocketMessage>(text)
        
        when (data.event) {
            "FRIEND_MOVED" -> {
                // Actualizar posición del amigo en el mapa
                updateFriendLocation(
                    data.data.username,
                    data.data.lat,
                    data.data.lon
                )
            }
            "FRIEND_DISCONNECTED" -> {
                // Remover amigo del mapa
                removeFriend(data.data.username)
            }
        }
    }
    
    override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
        println("Error: ${t.message}")
    }
})

// Enviar tu ubicación
fun sendLocation(lat: Double, lon: Double) {
    val message = Json.encodeToString(mapOf(
        "event" to "UPDATE_LOCATION",
        "data" to mapOf("lat" to lat, "lon" to lon)
    ))
    webSocket.send(message)
}
```

---

## 🐛 Troubleshooting

### API no responde

```bash
docker-compose logs api
docker-compose restart api
```

### WebSocket no conecta

1. Verificar que nginx esté corriendo: `docker-compose ps nginx`
2. Ver logs de nginx: `docker-compose logs nginx`
3. Probar directamente a la API: `ws://tu-ip:8000/ws/TEST/user`

### Base de datos no conecta

```bash
# Ver logs
docker-compose logs db

# Verificar que esté healthy
docker-compose ps

# Reiniciar
docker-compose restart db
```

### Puerto ocupado

```bash
# Ver qué usa el puerto 80
sudo lsof -i :80

# Detener nginx del sistema
sudo systemctl stop nginx
```

---

## 🔐 Security Checklist

- [ ] Cambiar `DB_ROOT_PASSWORD` y `DB_PASSWORD`
- [ ] Generar nuevo `SECRET_KEY` único
- [ ] Configurar HTTPS con certificado válido
- [ ] Configurar firewall en EC2 Security Groups
- [ ] No exponer puerto 3306 (MySQL) públicamente
- [ ] Actualizar `allow_origins` en CORS para tu app Android
- [ ] Configurar backups automáticos de MySQL
- [ ] Habilitar logs de auditoría

---

## 📊 Monitoreo

```bash
# Ver uso de recursos
docker stats

# Ver uso de disco
docker system df

# Health check cada 5 minutos
crontab -e
# Agregar:
*/5 * * * * curl -f http://localhost/health || docker-compose restart api
```

---

## 🎉 ¡Listo!

Tu API está desplegada con:
- ✅ MySQL para usuarios
- ✅ JWT Authentication
- ✅ WebSocket para ubicación en tiempo real
- ✅ Nginx como proxy reverso
- ✅ Docker Compose orquestando todo

**URLs importantes:**
- API: `http://tu-ip-elastica/`
- Docs: `http://tu-ip-elastica/docs`
- WebSocket: `ws://tu-ip-elastica/ws/{code}/{username}`

Con HTTPS:
- API: `https://tu-dominio.com/`
- WebSocket: `wss://tu-dominio.com/ws/{code}/{username}`
