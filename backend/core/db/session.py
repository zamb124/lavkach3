import asyncio
import os
import uuid
from contextvars import ContextVar, Token
from idlelib.pyparse import trans
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
from core.helpers.broker import list_brocker
from core.db_config import config, TestConfig
from httpx import AsyncClient as asyncclient

from core.helpers.cache import CacheTag

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
session_context: ContextVar[str] = ContextVar("session_context")


def get_session_context() -> str:
    session_id = session_context.get()
    logger.info(f"Context get: {session_id}")
    return session_id

def set_session_context(session_id: str) -> Token:
    logger.info(f"Context set: {session_id}")
    return session_context.set(session_id)

def reset_session_context(context: Token) -> None:
    session_context.reset(context)
    logger.info("Context reset")

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
    expire_on_commit=False if isinstance(config, TestConfig) else True
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

    async def prepare_bus(self, entity: object, method: str, updated_fields:list = None):
        return {
            'cache_tag': CacheTag.MODEL,
            'message': f'{self.__tablename__.capitalize()} is {method.capitalize()}',
            'company_id': entity.company_id if hasattr(entity,  'company_id') else entity.id,
            'vars': {
                'id': entity.id,
                'lsn': entity.lsn if method == 'update' else None,
                'model': self.__tablename__,
                'method': method,
                'updated_fields': updated_fields
            }
        }

    @list_brocker.task(queue_name='model')
    async def update_notify(model: str, data: dict):
        print('alalala')
        client = asyncclient()
        responce = await client.post(
            url=f'http://{config.BUS_HOST}:{config.BUS_PORT}/api/bus/bus',
            json=data,
            headers={'Authorization': config.INTERCO_TOKEN},
            timeout=1
        )
        if responce.status_code == 200:
            logger.info(f'Message sended to bus.bus')
        else:
            logger.warning(responce.text)


    async def notify(self, method, updated_fields: list = None, message=None):
        if not message:
            message = await self.prepare_bus(self, method=method, updated_fields=updated_fields)
        i: int = 1
        while True:
            try:
                if os.environ.get('ENT') == 'test':
                    break
                task = await self.update_notify.kiq(self.__tablename__, message)
                logger.info(f'Message sended to bus.bus with id: {task.task_id}')
                break
            except Exception as ex:
                i += 1
                await asyncio.sleep(5)
                logger.error(f'Error while sending message to bus.bus: {ex}')
                logger.error(f'Try to send message again to bus.bus: {i}..')
            if i > 20:
                break

