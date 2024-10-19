from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, Request, Depends
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.requests import HTTPConnection
from starlette.types import ASGIApp, Scope, Receive, Send

from .bus_tasks import start_processing_messages
from .tkq import broker
from .bus_router import bus_router
from ...db_config import config
from ...env import Env
from ...exceptions import CustomException
from ...fastapi.dependencies import Logging
from ...fastapi.middlewares import (
    AuthenticationMiddleware,
    AuthBackend,
    SQLAlchemyMiddleware,
)
from ...helpers.cache import Cache, CustomKeyMaker
from ...helpers.cache import RedisBackend
from . import __domain__ as bus_domain
domains = [bus_domain]

env = None

class EnvMidlleWare:
    """
    Адартер кладется в request для удобства обращений к обьектам сервисов
    """
    def __init__(self, app: ASGIApp, *args, **kwargs):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        global env
        if scope['type'] in ("http", "websocket"):
            conn = HTTPConnection(scope)
            if not env:
                env = Env(domains, conn)
                scope['env'] = env
            else:
                scope['env'] = env
                env.request = conn
        await self.app(scope, receive, send)


def init_routers(app_: FastAPI) -> None:
    app_.include_router(bus_router)



def init_listeners(app_: FastAPI) -> None:
    # Exception handler
    @app_.exception_handler(CustomException)
    async def custom_exception_handler(request: Request, exc: CustomException):
        return JSONResponse(
            status_code=exc.code,
            content={"error_code": exc.error_code, "message": exc.message},
        )


def on_auth_error(request: Request, exc: Exception):
    status_code, error_code, message = 401, None, str(exc)
    if isinstance(exc, CustomException):
        status_code = int(exc.code)
        error_code = exc.error_code
        message = exc.message

    return JSONResponse(
        status_code=status_code,
        content={"error_code": error_code, "message": message},
    )

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
        Старт сервера
    """
    await start_processing_messages()
    await broker.startup()
    yield
    """
            Выключение сервера
    """
    await broker.shutdown()


def make_middleware() -> List[Middleware]:
    middleware = [
        Middleware(EnvMidlleWare),
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=False,
            allow_methods=["*"],
            allow_headers=["*"],
        ),
        Middleware(
            AuthenticationMiddleware,
            backend=AuthBackend(),
            on_error=on_auth_error,
        ),
        Middleware(SQLAlchemyMiddleware),
    ]
    return middleware


def init_cache() -> None:
    Cache.init(backend=RedisBackend(), key_maker=CustomKeyMaker())


def create_app() -> FastAPI:
    app_ = FastAPI(
        lifespan=lifespan,
        title="BUS",
        description="Hide API",
        version="1.0.0",
        docs_url=None if config.ENV == "production" else "/api/bus/docs",
        redoc_url=None if config.ENV == "production" else "/api/bus/redoc",
        dependencies=[Depends(Logging)],
        middleware=make_middleware(),
    )
    init_routers(app_=app_)
    init_listeners(app_=app_)
    init_cache()
    return app_


app = create_app()
