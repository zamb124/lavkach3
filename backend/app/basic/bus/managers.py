from datetime import datetime

from fastapi import WebSocket
from pydantic import UUID4

from core.helpers.cache import RedisBackend
from core.helpers.redis import redis
from core.helpers.cache.cache_manager import Cache
class ConnectionManager:
    cache: Cache

    def __init__(self):
        self.cache = Cache
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        cache_key = await self.cache.set_maker(prefix='session', key=user_id, responce={'session_start': datetime.now().isoformat()})
        self.active_connections[cache_key] = websocket

    async def disconnect(self, user_id: str):
        await self.cache.backend.delete(f'ws-{user_id}')
        self.active_connections.pop(f'session::{user_id}')

    async def send_personal_message(self, message: dict, user_id: str):
        if websocket := self.active_connections.get(f'session::{user_id}'):
            await websocket.send_json(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            await connection.send_text(message)


ws_manager = ConnectionManager()
