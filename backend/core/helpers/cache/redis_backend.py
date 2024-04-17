import pickle
from typing import Any, Optional

import ujson

from core.helpers.cache.base import BaseBackend
from core.helpers.redis import redis as redis_client


class RedisBackend(BaseBackend):
    async def get(self, *, key: str) -> Any:
        result = await redis_client.get(key)
        if not result:
            return

        return ujson.loads(result)

    async def set(self, *, response: Any, key: str, ttl: int = 60) -> None:
        if isinstance(response, dict):
            response = ujson.dumps(response)
        else:
            response = pickle.dumps(response)

        await redis_client.set(name=key, value=response, ex=ttl)

    async def set_hash(
            self,
            name: str,
            key: Optional[str] = None,
            value: Optional[str] = None,
            mapping: Optional[dict] = None,
            items: Optional[list] = None,
    ) -> None:
        await redis_client.hset(name=name, key=key, value=value, mapping=mapping, items=items)

    async def delete_startswith(self, *, key: str) -> None:
        async for key in redis_client.scan_iter(f"{key}*"):
            await redis_client.delete(key)

    async def get_startswith(self, *, key: str) -> dict:
        keys = []
        data = {}
        async for value in redis_client.scan_iter(f"{key}*"):
            keys.append(value)
        for key in keys:
            data.update({
                key.decode('utf-8'): await self.get(key=key)
            })
        return data

    async def delete(self, *, key: str) -> None:
        await redis_client.delete(key)


redis_backend = RedisBackend()
