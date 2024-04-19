from datetime import datetime

from fastapi import WebSocket

from core.helpers.cache import CacheTag
from core.helpers.cache.cache_manager import Cache


class ConnectionManager:
    cache: Cache

    def __init__(self):
        self.cache = Cache
        self.active_connections: dict[dict[str: WebSocket, str: int]] = {}

    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        cache_key = await self.cache.set(tag=CacheTag.WS_SESSION, key=user_id, response={'session_start': datetime.now().isoformat()})
        self.active_connections[cache_key] = websocket

    async def disconnect(self, user_id: str):
        await self.cache.remove_by_tag(tag=CacheTag.WS_SESSION, key=user_id)
        self.active_connections.pop(f'{CacheTag.WS_SESSION.value}:{user_id}')

    async def send_personal_message(self, message: str, user_id: str, message_type='other'):
        if websocket := self.active_connections.get(f'{CacheTag.WS_SESSION.value}:{user_id}'):
            await websocket.send_json({
                'message_type': message_type,
                'message': message
            })

    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            await connection.send_text(message)


ws_manager = ConnectionManager()


