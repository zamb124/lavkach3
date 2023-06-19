import redis.asyncio as aioredis

from backend.core.config import config

redis = aioredis.from_url(url=f"redis://{config.REDIS_HOST}")
