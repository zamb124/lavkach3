import json
from typing import Annotated

from fastapi import APIRouter, Depends, WebSocketException
from fastapi import Request
from fastapi.responses import HTMLResponse
from starlette import status
from starlette.websockets import WebSocket, WebSocketDisconnect

from app.bff.template_spec import templates
from core.fastapi.frontend.constructor import ClassView
from core.fastapi.middlewares import AuthBackend

inventory_app = APIRouter()


@inventory_app.get("", response_class=HTMLResponse)
async def move(request: Request):
    """Список перемещений"""
    cls = await ClassView(request, 'order_type')
    template = f'inventory/app/app{"" if request.scope["htmx"].hx_request else "-full"}.html'
    return templates.TemplateResponse(request, template, context={'cls': cls})


async def get_token(websocket: WebSocket):
    _, user = await AuthBackend().authenticate(websocket)
    return user


users: dict = {

}


@inventory_app.websocket("")
async def connect(websocket: WebSocket, user: Annotated[str, Depends(get_token)]):
    """
            API получение сообщений
        """
    if not user.user_id:  # type: ignore
        raise WebSocketException(code=status.HTTP_401_UNAUTHORIZED)
    try:
        session = users.get(user.user_id)  # type: ignore
        await websocket.accept()
        if not session:
            session = {  # type: ignore
                'socket': websocket,
                'address': None
            }
            users.update({user.user_id: session})
        else:
            session['socket'] = websocket
        if not session['address']:
            cls = await ClassView(websocket,  'order_type', key=websocket.query_params.get('key'))
            await cls.init()
            responce_text = cls.as_card_kanban
        else:
            cls = await ClassView(websocket, session['address']['model'], key=websocket.query_params.get('key'))
            await cls.init(params={f'{session["address"]["model"]}_id__in': [session['address']['id']]})
            responce_text  = cls.as_card_list
        await session['socket'].send_text(responce_text)
        while True:
            message = await session['socket'].receive_json()
            if message.get('back'):
                session['address'] = None
                cls = await ClassView(
                    websocket, 'order_type',
                    key=websocket.query_params.get('key'),
                    vars={
                        'button_update': False,
                        'button_view': True
                    }
                )
                await cls.init()
                await session['socket'].send_text(cls.as_card_kanban)
            if message.get('model') == 'order_type':
                cls = await ClassView(websocket, key=message['class_key'], model='order')
                await cls.init(params={'order_type_id__in': [message['id']]})
                session['address'] = {
                    'model': 'order_type',
                    'id': message['id']
                }
                await session['socket'].send_text(cls.as_card_list)
            elif message.get('model') == 'order':
                cls = await ClassView(websocket, key=message['class_key'], model='move')
                await cls.init(params={'order_id__in': [message['id']]})
                await session['socket'].send_text(cls.as_card_list)

    except WebSocketDisconnect:
        session.pop('socket')
    except Exception as e:
        session.pop('socket')
        a=1
