import logging
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import List

from fastapi import FastAPI, Request, Depends
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.requests import HTTPConnection
from starlette.types import ASGIApp, Scope, Receive, Send

from app.bff.bff_router import bff_router
from app.bff.bff_tasks import remove_expired_tokens
from app.bff.tkq import broker
from core.db_config import config
from core.env import Env, domains
from core.exceptions import CustomException
from core.fastapi.dependencies import Logging
from core.fastapi.middlewares import (
    AuthenticationMiddleware,
    AuthBffBackend,
    SQLAlchemyMiddleware,
)
from core.helpers.cache import Cache, CustomKeyMaker
from core.helpers.cache import RedisBackend
from core.utils.timeit import add_timing_middleware

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Htmx:
    hx_target: str = None
    hx_current_url: str = None
    hx_request: bool = None


class HTMXMidlleWare:
    """
    Адартер кладется в request для удобства htmx переменных
    """

    def __init__(self, app: ASGIApp, *args, **kwargs):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope['type'] in ("http", "websocket"):
            conn = HTTPConnection(scope)
            scope['htmx'] = Htmx(
                hx_target=conn.headers.get('hx-target'),
                hx_current_url=conn.headers.get('hx-current-url'),
                hx_request=True if conn.headers.get('hx-request') == 'true' else False
            )
        await self.app(scope, receive, send)


class EnvMidlleWare:
    """
    Адартер кладется в request для удобства обращений к обьектам сервисов
    """

    def __init__(self, app: ASGIApp, *args, **kwargs):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope['type'] in ("http", "websocket"):
            conn = HTTPConnection(scope)
            scope['env'] = Env(domains, conn)
        await self.app(scope, receive, send)


def init_routers(app_: FastAPI) -> None:
    app_.include_router(bff_router)


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
        Middleware(HTMXMidlleWare),
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=False,
            allow_methods=["*"],
            allow_headers=["*"],
        ),
        Middleware(
            AuthenticationMiddleware,
            backend=AuthBffBackend(),
            on_error=on_auth_error,
        ),
        Middleware(SQLAlchemyMiddleware),

    ]
    return middleware


def init_cache() -> None:
    Cache.init(backend=RedisBackend(), key_maker=CustomKeyMaker())


def fake_answer_to_everything_ml_model(x: float):
    return x * 42


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
        Старт сервера
    """
    await remove_expired_tokens()
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
        docs_url=None if config.ENV == "production" else "/docs",
        redoc_url=None if config.ENV == "production" else "/redoc",
        dependencies=[Depends(Logging)],
        middleware=make_middleware(),
    )
    init_routers(app_=app_)
    init_listeners(app_=app_)
    init_cache()
    return app_


app = create_app()

add_timing_middleware(app, record=logger.info, prefix="bff", exclude="untimed")
app.mount("/static", StaticFiles(directory="app/bff/static"), name="static")
