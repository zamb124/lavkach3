from contextlib import asynccontextmanager
from typing import List

import taskiq_fastapi
from fastapi import FastAPI, Request, Depends
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.requests import HTTPConnection
from starlette.types import ASGIApp, Scope, Receive, Send

from app.inventory.inventory_config import config as app_config
from app.inventory.inventory_router import inventory_router
from core.db_config import config
from core.env import Env, domains
from core.exceptions import CustomException
from core.fastapi.dependencies import Logging
from core.fastapi.middlewares import (
    AuthenticationMiddleware,
    AuthBackend,
    SQLAlchemyMiddleware,
)
from core.helpers.broker import broker
from core.helpers.cache import Cache, CustomKeyMaker
from core.helpers.cache import RedisBackend


class EnvMidlleWare:
    """
    Адартер кладется в request для удобства
    """

    def __init__(self, app: ASGIApp, *args, **kwargs):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope['type'] in  ("http", "websocket"):
            conn = HTTPConnection(scope)
            scope['env'] = Env(domains, conn, broker)
        await self.app(scope, receive, send)

def init_routers(app_: FastAPI) -> None:
    app_.include_router(inventory_router)


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

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
        Старт сервера
    """
    await broker.startup()
    yield
    """
            Выключение сервера
    """
    await broker.shutdown()
def create_app() -> FastAPI:
    app_ = FastAPI(
        lifespan=lifespan,
        title="Hide",
        description="Hide API",
        version="1.0.0",
        docs_url=None if config.ENV == "production" else "/api/inventory/docs",
        redoc_url=None if config.ENV == "production" else "/api/inventory/redoc",
        dependencies=[Depends(Logging)],
        middleware=make_middleware(),
    )
    init_routers(app_=app_)
    init_listeners(app_=app_)
    init_cache()
    return app_


app = create_app()
taskiq_fastapi.init(broker, app_config.BROKER_PATH)
