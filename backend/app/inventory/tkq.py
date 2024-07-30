from uuid import uuid4

from taskiq_redis import ListQueueBroker, RedisAsyncResultBackend

from core.db.session import set_session_context
from core.helpers.broker.initializator import init


class InventoryQueueBroker(ListQueueBroker):
    @property
    def env(self):
        """
            Возвращает ENV для тасков
        """
        request = self.custom_dependency_context['request']
        app = request.app
        env = app.extra['env']['cls'](app.extra['env']['domains'], request, broker)
        session_id = str(uuid4())
        set_session_context(session_id=session_id)
        return env

redis_async_result = RedisAsyncResultBackend(
    redis_url="rediss://default:AVNS_w6X_JVOCj6vbTjwIowO@redis-do-user-15109425-0.c.db.ondigitalocean.com:25061",
    result_ex_time=1000,  # Сколько хранить результаты в секундах
    ssl_cert_reqs=None,
    socket_timeout=360
)

# Or you can use PubSubBroker if you need broadcasting
broker = InventoryQueueBroker(
    url="rediss://default:AVNS_w6X_JVOCj6vbTjwIowO@redis-do-user-15109425-0.c.db.ondigitalocean.com:25061",
    ssl_cert_reqs=None,
    socket_timeout=360,
    queue_name="inventory_queue"
).with_result_backend(redis_async_result)

init(broker, "app.inventory.inventory_server:app")

# broker = InMemoryBroker()
