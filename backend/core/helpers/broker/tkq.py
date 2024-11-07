import asyncio
from contextvars import ContextVar
from uuid import uuid4
import importlib
from taskiq import SimpleRetryMiddleware, TaskiqMiddleware
from taskiq_redis import ListQueueBroker, RedisAsyncResultBackend, PubSubBroker

from core.db_config import config
from core.helpers.broker.initializator import init
import taskiq.receiver
class TaskSession(TaskiqMiddleware):
    """Middleware to add retries."""

    def __init__(self,) -> None:
        ...

    def pre_execute(
            self,
            message: "TaskiqMessage",
    ) -> "Union[TaskiqMessage, Coroutine[Any, Any, TaskiqMessage]]":
        return message

    async def on_error(
        self,
        message: "TaskiqMessage",
        result: "TaskiqResult[Any]",
        exception: BaseException,
    ) -> "Union[None, Coroutine[Any, Any, None]]":
        ...


redis_async_result = RedisAsyncResultBackend(
    redis_url=f"redis{'s' if config.REDIS_SSL else ''}://default:{config.REDIS_PASSWORD}@{config.REDIS_HOST}:{config.REDIS_PORT}",
    result_ex_time=60,  # Сколько хранить результаты в секундах
    socket_timeout=360
)

# Or you can use PubSubBroker if you need broadcasting
list_brocker = ListQueueBroker(
    url=f"redis{'s' if config.REDIS_SSL else ''}://default:{config.REDIS_PASSWORD}@{config.REDIS_HOST}:{config.REDIS_PORT}",
    queue_name='model',
    socket_timeout=360
).with_result_backend(redis_async_result).with_middlewares(SimpleRetryMiddleware(default_retry_count=3)).with_middlewares(TaskSession())
init(list_brocker, 'core.env:Env')
#
# async def main():
#     async with broker:
#         await broker.send_task("core.tasks:task", args=(1, 2), kwargs={"a": 3, "b": 4})
#
# if __name__ == "__main__":
#     asyncio.run(main())


