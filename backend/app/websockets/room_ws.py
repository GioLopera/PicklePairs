from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter(tags=["websocket"])


class ConnectionManager:
    def __init__(self):
        # room_code → list of active WebSocket connections
        self._connections: dict[str, list[WebSocket]] = {}

    async def connect(self, room_code: str, websocket: WebSocket):
        await websocket.accept()
        self._connections.setdefault(room_code, []).append(websocket)

    def disconnect(self, room_code: str, websocket: WebSocket):
        connections = self._connections.get(room_code, [])
        if websocket in connections:
            connections.remove(websocket)
        if not connections:
            self._connections.pop(room_code, None)

    async def broadcast(self, room_code: str, message: dict):
        """Send a JSON message to all clients connected to a room."""
        for websocket in list(self._connections.get(room_code, [])):
            try:
                await websocket.send_json(message)
            except Exception:
                # Client disconnected mid-broadcast — clean up silently
                self.disconnect(room_code, websocket)


manager = ConnectionManager()


@router.websocket("/ws/{room_code}")
async def websocket_endpoint(websocket: WebSocket, room_code: str):
    await manager.connect(room_code, websocket)
    try:
        while True:
            # Keep the connection alive; clients are receive-only in MVP
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(room_code, websocket)
