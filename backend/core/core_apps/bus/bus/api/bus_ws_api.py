from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    status,
    WebSocket,
    WebSocketDisconnect,
    WebSocketException,
)

from ...bus.managers import ws_manager
from core.fastapi.middlewares import AuthBackend
from ...bus_tasks import logger

ws_router = APIRouter()


async def get_token(websocket: WebSocket):
    logger.warning(websocket.headers)
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
                user.user_id,  # type: ignore
            )
    except WebSocketDisconnect as ex:
        logger.error(f"websocket disconnected: {user.nickname} {str(ex)}")
        await ws_manager.disconnect(session_key)

