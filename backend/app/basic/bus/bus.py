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
from starlette.requests import Request

from core.db.session import session
from app.basic.bus.managers import ws_manager
from core.fastapi.middlewares import AuthBackend

ws_router = APIRouter()


async def get_token(websocket: WebSocket):
    _, user = await AuthBackend().authenticate(websocket)
    return user


@ws_router.websocket("/ws/bus")
async def websocket_endpoint(websocket: WebSocket, user: Annotated[str, Depends(get_token)],):
    """
        API получение сообщений
    """
    if not user.user_id:
        raise WebSocketException(code=status.HTTP_401_UNAUTHORIZED)
    try:

        await ws_manager.connect(user.user_id, websocket)
        await ws_manager.send_personal_message("connection accepted", user.user_id,)
        while True:
            message = await websocket.receive_text()

            await ws_manager.send_personal_message(
                {"message": message},
                user.user_id,
            )
    except WebSocketDisconnect:
        await ws_manager.disconnect(user.user_id)
