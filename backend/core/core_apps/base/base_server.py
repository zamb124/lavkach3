from contextlib import asynccontextmanager
from typing import List

import uvicorn
from fastapi import FastAPI, Request, Depends
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.requests import HTTPConnection
from starlette.types import ASGIApp, Scope, Receive, Send

from core.core_apps.base.base_router import base_router
from core.db_config import config
from core.env import Env
from core.core_apps.base import __domain__ as base_domain
from core.exceptions import CustomException
from core.fastapi.dependencies import Logging
from core.fastapi.middlewares import (
    AuthenticationMiddleware,
    AuthBackend,
    SQLAlchemyMiddleware,
)
from core.helpers.broker.tkq import list_brocker
from core.helpers.cache import Cache, CustomKeyMaker
from core.helpers.cache import RedisBackend

domains = [base_domain]

class EnvMidlleWare:
    """
    Адартер кладется в request для удобства
    """

    def __init__(self, app: ASGIApp, *args, **kwargs):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope['type'] in  ("http", "websocket"):
            conn = HTTPConnection(scope)
            scope['env'] = Env(domains, conn)
        await self.app(scope, receive, send)


def init_routers(app_: FastAPI) -> None:
    app_.include_router(base_router)



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
    if not list_brocker.is_worker_process:
        await list_brocker.startup()
    yield
    """
            Выключение сервера
    """
    if not list_brocker.is_worker_process:
        await list_brocker.shutdown()

def create_app() -> FastAPI:
    app_ = FastAPI(
        title="Hide",
        lifespan=lifespan,
        description="Hide API",
        dependencies=[Depends(Logging)],
        middleware=make_middleware(),
    )
    init_routers(app_=app_)
    init_listeners(app_=app_)
    init_cache()
    return app_


app = create_app()
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8999, log_level="info")