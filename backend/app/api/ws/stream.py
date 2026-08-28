from typing import Dict, List, Set
from fastapi import WebSocket, WebSocketDisconnect
from app.models.events import SimulationEvent

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, session_id: str, websocket: WebSocket):
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = set()
        self.active_connections[session_id].add(websocket)

    def disconnect(self, session_id: str, websocket: WebSocket):
        if session_id in self.active_connections:
            self.active_connections[session_id].discard(websocket)
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]

    async def broadcast_event(self, session_id: str, event: SimulationEvent):
        if session_id in self.active_connections:
            data = event.model_dump(mode="json")
            dead_sockets = set()
            for ws in self.active_connections[session_id]:
                try:
                    await ws.send_json(data)
                except Exception:
                    dead_sockets.add(ws)
            for dead in dead_sockets:
                self.active_connections[session_id].discard(dead)

manager = ConnectionManager()

