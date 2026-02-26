from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
from typing import Dict, List

router = APIRouter()

# Diccionario para guardar las conexiones vivas: { "UPCH77": [websocket1, websocket2] }
# (Si él ya tiene un RoomManager, puede mover este diccionario ahí)
active_connections: Dict[str, List[WebSocket]] = {}

@router.websocket("/ws/{room_code}/{username}")
async def radar_websocket(websocket: WebSocket, room_code: str, username: str):
    # Aceptar la conexión del celular
    await websocket.accept()
    
    # Crear la sala si no existe en las conexiones activas
    if room_code not in active_connections:
        active_connections[room_code] = []
    
    active_connections[room_code].append(websocket)
    
    try:
        # Bucle infinito escuchando lo que manda tu celular Android
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            
            # Si recibe tu ubicación...
            if payload.get("event") == "UPDATE_LOCATION":
                
                # Prepara el JSON para reenviarlo (El contrato que tú esperas en Android)
                response = {
                    "event": "FRIEND_MOVED",
                    "data": {
                        "username": username,
                        "lat": payload["data"].get("lat"),
                        "lon": payload["data"].get("lon")
                    }
                }
                
                # Se lo manda a TODOS los que estén en la sala, EXCEPTO al que lo mandó
                for connection in active_connections[room_code]:
                    if connection != websocket:
                        await connection.send_text(json.dumps(response))

    except WebSocketDisconnect:
        # Si el usuario cierra la app o pierde internet, lo sacamos de la sala
        if websocket in active_connections.get(room_code, []):
            active_connections[room_code].remove(websocket)
        
        # Si la sala quedó vacía, la borramos para no gastar memoria RAM
        if not active_connections.get(room_code):
            if room_code in active_connections:
                del active_connections[room_code]
        else:
            # Si alguien sigue en la sala, le avisamos que su amigo se fue (Tu Rollback optimista)
            disconnect_msg = {
                "event": "FRIEND_DISCONNECTED",
                "data": {"message": f"{username} se ha desconectado"}
            }
            for connection in active_connections[room_code]:
                await connection.send_text(json.dumps(disconnect_msg))