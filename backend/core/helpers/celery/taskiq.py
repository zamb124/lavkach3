import taskiq_fastapi
from fastapi_app.settings import settings
from taskiq import InMemoryBroker
from taskiq_nats import NatsBroker
from taskiq_redis import RedisAsyncResultBackend

broker = NatsBroker(
    settings.nats_urls.split(","),
    queue="fastapi_app_queue",
).with_result_backend(
    RedisAsyncResultBackend(settings.redis_url),
)

# Actually, you can remove this line and test agains real
# broker. Which is more preferable in some cases.
if settings.env.lower() == "pytest":
    broker = InMemoryBroker()


taskiq_fastapi.init(broker, "fastapi_app.__main__:get_app")