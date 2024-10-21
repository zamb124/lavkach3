from datetime import datetime

from fastapi import WebSocket

from core.core_apps.bus.bus_tasks import logger
from core.helpers.cache import CacheTag
from core.helpers.cache.cache_manager import Cache


class ConnectionManager:
    cache: Cache

    def __init__(self):
        self.cache = Cache
        self.active_connections: dict[dict[str: WebSocket, str: int]] = {}

    async def connect(self, session_key: str, websocket: WebSocket):
        await websocket.accept()
        cache_key = await self.cache.set(tag=CacheTag.WS_SESSION, key=session_key, response={'session_start': datetime.now().isoformat()})
        self.active_connections[cache_key] = websocket

    async def disconnect(self, session_key: str):
        await self.cache.remove_by_tag(tag=CacheTag.WS_SESSION, key=session_key)
        keys_to_delete = [
            key for key, socket in
            self.active_connections.items()
            if key.startswith(f'{CacheTag.WS_SESSION.value}:{session_key}')
        ]
        for key_to_del in keys_to_delete:
            logger.warning(f"Disconnecting {key_to_del}")
            self.active_connections.pop(key_to_del)

    async def send_personal_message(self, message: str, user_id: str, message_type='other'):
        sockets = [
            socket for key, socket in
            self.active_connections.items()
            if key.startswith(f'{CacheTag.WS_SESSION.value}:{user_id}')
        ]
        for sock in sockets:
            await sock.send_json({
                'message_type': message_type,
                'message': message
            })
    async def send_tagged_message(self,websocket, tag: CacheTag, message:str, vars: dict[str: str]):
            await websocket.send_json({
                'tag': tag.name,
                'message': message,
                'vars': vars
            })

    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            await connection.send_text(message)


ws_manager = ConnectionManager()


