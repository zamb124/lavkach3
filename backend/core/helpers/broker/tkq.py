import os
import uuid

from taskiq import SimpleRetryMiddleware, TaskiqMiddleware, InMemoryBroker
from taskiq_redis import ListQueueBroker, RedisAsyncResultBackend

from core.context import set_session_context
from core.db_config import config
from core.helpers.broker.initializator import init


class TaskSession(TaskiqMiddleware):
    """Middleware to add retries."""

    def __init__(self,) -> None:
        ...

    def pre_execute(self, message: "TaskiqMessage"):  # type: ignore
        if message.labels.get('type') == 'service_method':
            # Если тип сообщения service_method, то меняем первый аргумент на сервис указанной при kiq
            model = message.args[0]
            model_service = self.broker.state.data['env'].get_env()[model].service
            message.args[0] = model_service
        session_id  = str(uuid.uuid4())
        set_session_context(session_id)
        return message

    def post_execute(self,message: "TaskiqMessage",result: "TaskiqResult[Any]"):
        ...

    async def on_error(self,message: "TaskiqMessage",result: "TaskiqResult[Any]",exception: BaseException):
        ...

    def post_save(self,message: "TaskiqMessage",result: "TaskiqResult[Any]"):
        ...

redis_async_result = RedisAsyncResultBackend(  # type: ignore
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

if os.environ.get('ENV') == 'test':
    list_brocker = InMemoryBroker().with_middlewares(SimpleRetryMiddleware(default_retry_count=3)).with_middlewares(TaskSession())# type: ignore
init(list_brocker, 'core.env:Env')
#
# async def main():
#     async with broker:
#         await broker.send_task("core.tasks:task", args=(1, 2), kwargs={"a": 3, "b": 4})
#
# if __name__ == "__main__":
#     asyncio.run(main())


