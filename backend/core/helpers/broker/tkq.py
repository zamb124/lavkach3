from contextvars import ContextVar
from uuid import uuid4

from taskiq import SimpleRetryMiddleware, TaskiqMiddleware
from taskiq_redis import ListQueueBroker, RedisAsyncResultBackend

from core.helpers.broker.initializator import init

class TaskSession(TaskiqMiddleware):
    """Middleware to add retries."""

    def __init__(self,) -> None:
        ...

    def pre_execute(
            self,
            message: "TaskiqMessage",
    ) -> "Union[TaskiqMessage, Coroutine[Any, Any, TaskiqMessage]]":
        a=1
        return message



redis_async_result = RedisAsyncResultBackend(
    redis_url="rediss://default:AVNS_w6X_JVOCj6vbTjwIowO@redis-do-user-15109425-0.c.db.ondigitalocean.com:25061",
    result_ex_time=1000,  # Сколько хранить результаты в секундах
    ssl_cert_reqs=None,
    socket_timeout=360
)

# Or you can use PubSubBroker if you need broadcasting
broker = ListQueueBroker(
    url="rediss://default:AVNS_w6X_JVOCj6vbTjwIowO@redis-do-user-15109425-0.c.db.ondigitalocean.com:25061",
    ssl_cert_reqs=None,
    socket_timeout=360
).with_result_backend(redis_async_result).with_middlewares(SimpleRetryMiddleware(default_retry_count=3)).with_middlewares(TaskSession())
init(broker, 'core.env:Env')


