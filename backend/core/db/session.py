from contextvars import ContextVar, Token
from typing import Union

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_scoped_session,
)
from sqlalchemy.orm import RelationshipProperty, registry, relationship
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql.expression import Update, Delete, Insert

from backend.core.config import config
from sqlalchemy.orm.decl_api import DeclarativeMeta
session_context: ContextVar[str] = ContextVar("session_context")


def get_session_context() -> str:
    return session_context.get()


def set_session_context(session_id: str) -> Token:
    return session_context.set(session_id)


def reset_session_context(context: Token) -> None:
    session_context.reset(context)


engines = {
    "writer": create_async_engine(config.WRITER_DB_URL, pool_recycle=3600),
    "reader": create_async_engine(config.READER_DB_URL, pool_recycle=3600),
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
