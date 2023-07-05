from functools import wraps
from typing import Type

from .base import BaseBackend, BaseKeyMaker
from core.helpers.cache.redis_backend import RedisBackend
from core.helpers.cache.custom_key_maker import CustomKeyMaker
from .cache_tag import CacheTag


class CacheManager:
    def __init__(self):
        self.backend = RedisBackend()
        self.key_maker = CustomKeyMaker()

    def init(self, backend: Type[BaseBackend], key_maker: Type[BaseKeyMaker]) -> None:
        self.backend = backend
        self.key_maker = key_maker

    async def set_maker(self, responce, key, prefix, ttl=360):
        key = await self.key_maker.make(function=key, prefix=prefix)
        await self.backend.set(responce, key, ttl)

    def cached(self, prefix: str = None, tag: CacheTag = None, ttl: int = 60):
        def _cached(function):
            @wraps(function)
            async def __cached(*args, **kwargs):
                if not self.backend or not self.key_maker:
                    raise Exception("backend or key_maker is None")

                key = await self.key_maker.make(
                    function=function,
                    prefix=prefix if prefix else tag.value,
                )
                cached_response = await self.get(key=key)
                if cached_response:
                    return cached_response

                response = await function(*args, **kwargs)
                await self.set(response=response, key=key, ttl=ttl)
                return response

            return __cached

        return _cached

    async def remove_by_tag(self, tag: CacheTag) -> None:
        await self.backend.delete_startswith(value=tag.value)

    async def remove_by_prefix(self, prefix: str) -> None:
        await self.backend.delete_startswith(value=prefix)


Cache = CacheManager()
