from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    Query,
    status,
    WebSocket,
    WebSocketDisconnect,
    WebSocketException,
)
from pydantic import BaseModel
from starlette.requests import Request

from app.bus.bus.services import BusService
from core.db.session import session
from app.bus.bus.managers import ws_manager
from core.fastapi.middlewares import AuthBackend
from core.helpers.cache import CacheTag

ws_router = APIRouter()


async def get_token(websocket: WebSocket):
    _, user = await AuthBackend().authenticate(websocket)
    return user


@ws_router.websocket("/bus")
async def websocket_endpoint(websocket: WebSocket, user: Annotated[str, Depends(get_token)],):
    """
        API получение сообщений
    """
    if not user.user_id:
        raise WebSocketException(code=status.HTTP_401_UNAUTHORIZED)
    try:
        session_key = f'{user.user_id}:{websocket.headers.get("sec-websocket-key")}'
        await ws_manager.connect(session_key, websocket)
        await ws_manager.send_personal_message("connection accepted", session_key)
        while True:
            message = await websocket.receive_text()
            await ws_manager.send_personal_message(
                {"message": message},
                user.user_id,
            )
    except WebSocketDisconnect:
        await ws_manager.disconnect(session_key)

