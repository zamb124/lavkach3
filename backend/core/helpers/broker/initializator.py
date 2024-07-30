import uuid
from typing import Awaitable, Callable

from fastapi import FastAPI, Request
from starlette.requests import HTTPConnection
from taskiq import AsyncBroker, TaskiqEvents, TaskiqState
from taskiq.cli.utils import import_object

#from core.fastapi.schemas import CurrentUser
from core.service_config import config

def startup_event_generator(
    broker: AsyncBroker,
    app_path: str,
) -> Callable[[TaskiqState], Awaitable[None]]:
    """
    Generate shutdown event.

    This function takes FastAPI application path
    and runs startup event on broker's startup.

    :param broker: current broker.
    :param app_path: fastapi application path.
    :returns: startup handler.
    """

    async def startup(state: TaskiqState) -> None:
        if not broker.is_worker_process:
            return
        env = import_object(app_path)
        state.env = env
        populate_dependency_context(broker, env)

    return startup


def shutdown_event_generator(
    broker: AsyncBroker,
) -> Callable[[TaskiqState], Awaitable[None]]:
    """
    Generate shutdown event.

    This function takes FastAPI application
    and runs shutdown event on broker's shutdown.

    :param broker: current broker.
    :return: shutdown event handler.
    """

    async def shutdown(state: TaskiqState) -> None:
        if not broker.is_worker_process:
            return
        await state.fastapi_app.router.shutdown()
        await state.lf_ctx.__aexit__(None, None, None)

    return shutdown


def init(broker: AsyncBroker, app_path: str) -> None:
    """
    Add taskiq startup events.

    This is the main function to integrate FastAPI
    with taskiq.

    It creates startup events for broker. So
    in worker processes all fastapi
    startup events will run.

    :param broker: current broker to use.
    :param app_path: path to fastapi application.
    """
    broker.add_event_handler(
        TaskiqEvents.WORKER_STARTUP,
        startup_event_generator(broker, app_path),
    )

    broker.add_event_handler(
        TaskiqEvents.WORKER_SHUTDOWN,
        shutdown_event_generator(broker),
    )


def populate_dependency_context(broker: AsyncBroker, app: FastAPI) -> None:
    """
    Создает пустышку Request для Taskiq.
    """
    scope = {
    'type' : 'http',
    'http_version' : '1.1',
    'scheme' : 'http',
    'root_path' : '',
    'headers' : [(b'Authorization', f'{config.INTERCO_TOKEN}'),],
    'state' : {},
    'method' : 'GET',
    'path' : '/',
    'raw_path' : b'/',
    'query_string' : b'',
    'app' : app,
    #'user': CurrentUser(id=uuid.uuid4(), is_admin=True)
    }
    request = Request(scope=scope)
    #scope['env'] = app.extra['env']['cls'](app.extra['env']['domains'], request, broker)
    broker.add_dependency_context(
        {
            'request': request,
        },
    )

