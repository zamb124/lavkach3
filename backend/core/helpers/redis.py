import redis.asyncio as aioredis
from core.config import config

redis = aioredis.StrictRedis(
    username='default',
    host=config.REDIS_HOST,
    port=config.REDIS_PORT,
    password=config.REDIS_PASSWORD,
    ssl=config.REDIS_SSL,
    ssl_ca_certs=config.REDIS_CERT_PATH,
    ssl_cert_reqs=None,
    socket_timeout=1
)
