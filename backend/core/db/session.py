from contextvars import ContextVar, Token
from typing import Union
import logging
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_scoped_session,
)
from sqlalchemy.orm import registry
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.orm.decl_api import DeclarativeMeta
from sqlalchemy.sql.expression import Update, Delete, Insert
from core.helpers.broker import broker
from core.db_config import config
from httpx import AsyncClient as asyncclient

from core.helpers.cache import CacheTag

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
session_context: ContextVar[str] = ContextVar("session_context")


def get_session_context() -> str:
    return session_context.get()


def set_session_context(session_id: str) -> Token:
    return session_context.set(session_id)


def reset_session_context(context: Token) -> None:
    session_context.reset(context)


engines = {
    "writer": create_async_engine(config.WRITER_DB_URL, echo=True, pool_recycle=3600, max_overflow=30),
    "reader": create_async_engine(config.READER_DB_URL, echo=True, pool_recycle=3600, max_overflow=30),
}


class RoutingSession(Session):
    def get_bind(self, mapper=None, clause=None, **kw):
        if self._flushing or isinstance(clause, (Update, Delete, Insert)):
            return engines["writer"].sync_engine
        else:
            return engines["reader"].sync_engine


async_session_factory = sessionmaker(
    class_=AsyncSession,
    sync_session_class=RoutingSession,
)
session: Union[AsyncSession, async_scoped_session] = async_scoped_session(
    session_factory=async_session_factory,
    scopefunc=get_session_context,
)

mapper_registry = registry()


class Base(metaclass=DeclarativeMeta):
    __abstract__ = True

    registry = mapper_registry
    metadata = mapper_registry.metadata

    __init__ = mapper_registry.constructor

    async def prepere_bus(self, entity: object, method: str):
        return {
            'cache_tag': CacheTag.MODEL,
            'message': f'{self.__tablename__.capitalize()} is {method.capitalize()}',
            'company_id': entity.company_id if hasattr(entity,  'company_id') else entity.id,
            'vars': {
                'id': entity.id,
                'lsn': entity.lsn,
                'model': self.__tablename__,
                'method': method,
            }
        }

    @broker.task
    async def update_notify(model: str, data: dict):

        client = asyncclient()
        responce = await client.post(
            url=f'http://{config.BUS_HOST}:{config.BUS_PORT}/api/bus/bus',
            json=data,
            headers={'Authorization': config.INTERCO_TOKEN}
        )
        if responce.status_code == 200:
            logger.info(f'Message sended to bus.bus')
        else:
            logger.warning(responce.text)


    async def notify(self, method):
        message = await self.prepere_bus(self, method)
        task = await self.update_notify.kiq(self.__tablename__, message)