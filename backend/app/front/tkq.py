import taskiq_fastapi
from taskiq import InMemoryBroker
#from taskiq_nats import NatsBroker

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


taskiq_fastapi.init(broker, "app.front.front_server:app")