import taskiq_fastapi
from taskiq import InMemoryBroker
from core.service_config import config
#from taskiq_nats import NatsBroker
from taskiq_redis import RedisAsyncResultBackend

#from fastapi_app.settings import settings

# broker = NatsBroker(
#     settings.nats_urls.split(","),
#     queue="fastapi_app_queue",
# ).with_result_backend(
#     RedisAsyncResultBackend(settings.redis_url),
# )
#
# # Actually, you can remove this line and test agains real
# # broker. Which is more preferable in some cases.

broker = InMemoryBroker()
