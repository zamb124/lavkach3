import logging
from contextvars import ContextVar, Token

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
