from typing import Annotated

from fastapi import APIRouter, Depends, WebSocketException
from fastapi import Request
from fastapi.responses import HTMLResponse
from jinja2_fragments import render_block
from starlette import status
from starlette.responses import RedirectResponse
from starlette.websockets import WebSocket, WebSocketDisconnect

from app.bff.template_spec import templates
from core.fastapi.frontend.constructor import ClassView
from core.fastapi.frontend.types import MethodType
from core.fastapi.middlewares import AuthBackend
from app.bff.template_spec import environment
inventory_app = APIRouter()


@inventory_app.get("", response_class=HTMLResponse)
async def move(request: Request):
    """Список перемещений"""
    if not request.user.user_id:
        return RedirectResponse(f"/basic/user/login?next={request.url.path}")
    cls = await ClassView(request, 'order_type')
    template = f'inventory/app/app{"" if request.scope["htmx"].hx_request else "-full"}.html'
    return templates.TemplateResponse(request, template, context={'cls': cls, 'is_app': True})


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
            cls = await ClassView(
                websocket,
                model='order_type',
                key=websocket.query_params.get('key'),
                vars={
                    'button_update': False,
                    'button_view': True
                })
            await cls.init()
            responce_text = cls.as_card_kanban
        else:
            cls = await ClassView(websocket, session['address']['model'], key=websocket.query_params.get('key'))
            await cls.init(params={f'{session["address"]["model"]}_id__in': [session['address']['id']]})
            responce_text = cls.as_card_list
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
                orders_template = render_block(
                    environment=environment,
                    template_name=f'inventory/app/orders.html',
                    block_name='as_list',
                    method=MethodType.UPDATE,
                    key=cls.key,
                    title=message.get('title'),
                    lines=cls.lines.lines,
                )
                await session['socket'].send_text(orders_template)
            elif message.get('model') == 'order':
                cls = await ClassView(websocket, key=message['class_key'], model='move')
                await cls.init(params={'order_id__in': [message['id']]})
                moves_template = render_block(
                    environment=environment,
                    template_name=f'inventory/app/moves.html',
                    block_name='as_list',
                    method=MethodType.UPDATE,
                    key=cls.key,
                    title=message.get('title'),
                    lines=cls.lines.lines,
                )
                await session['socket'].send_text(moves_template)

    except WebSocketDisconnect:
        session.pop('socket')
    except Exception as e:
        raise e
