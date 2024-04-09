import redis.asyncio as aioredis
from core.config import config

redis = aioredis.from_url(url=f"redis://{config.REDIS_HOST}:{config.REDIS_PORT}")
redis = aioredis.StrictRedis(
    username='default',
    host=config.REDIS_HOST,
    port=config.REDIS_PORT,
    password=config.REDIS_PASSWORD,
    ssl=config.REDIS_SSL,
    ssl_ca_certs=config.REDIS_CERT_PATH,
    ssl_cert_reqs=None
)
#redis = aioredis.from_url('rediss://default:AVNS_w6X_JVOCj6vbTjwIowO@redis-do-user-15109425-0.c.db.ondigitalocean.com:25061', )
