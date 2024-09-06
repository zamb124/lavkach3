import asyncio
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Annotated, Optional
import traceback
from fastapi import APIRouter, Depends, WebSocketException
from fastapi import Request
from fastapi.responses import HTMLResponse
from jinja2_fragments import render_block
from pydantic import BaseModel, UUID4
from starlette import status
from starlette.responses import RedirectResponse
from starlette.websockets import WebSocket, WebSocketDisconnect

from app.bff.template_spec import environment
from app.bff.template_spec import templates
from core.env import Env
from core.frontend.constructor import ClassView
from core.fastapi.middlewares import AuthBackend
from core.fastapi.schemas import CurrentUser

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


users: dict[str, 'InventoryAPP'] = {

}
kill_task = None


async def kill_sessions():
    while True:
        to_del = []
        for user_id, app in users.items():
            if app.last_activity < datetime.now() - timedelta(seconds=1000):
                await app.websocket.close()
                to_del.append(user_id)
        for i in to_del:
            users.pop(i, None)
        await asyncio.sleep(30)


def _get_key() -> str:
    """Генерирует уникальный идетификатор для конструктора модели"""
    return f'A{uuid.uuid4().hex[:10]}'


class MessageType(str, Enum):
    MODEL: str = 'model'
    BARCODE: str = 'barcode'
    BACK: str = 'back'
    UPDATE: str = 'update'
    ACTION: str = 'action'


class Message(BaseModel):
    HEADERS: dict
    type: MessageType = MessageType.MODEL
    model: Optional[str] = None
    id: Optional[UUID4] = None
    barcode: Optional[str] = None
    mode: Optional[str] = None
    value: Optional[str] = None

    class Config:
        extra = 'allow'


class InventoryAPP:
    class_key: str
    user: CurrentUser
    store_id = str
    history: list = []
    websocket: WebSocket
    env: Env
    permissions: dict = {}
    current_page: str
    last_activity: datetime = datetime.now()
    pages: dict = {
        'order_type': 'get_orders_by_order_type',
        'order': 'get_moves_by_order_id',
        'move': 'get_suggests_by_move_id',
    }
    scan_methods: dict = {
        None: 'common_scan_method',
        'order_type': 'search_order_by_barcode',
        'order': 'search_move_by_barcode',
        'move': 'suggest_scan_method'
    }
    actions: dict = {
        'order_start': 'action_order_start',
        'order_finish': 'action_order_finish',
        'suggest_done': 'action_suggest_done'
    }
    model_templates: dict = {
        'order': {
            'as_card': 'inventory/app/order.html'
        }
    }

    async def send_error(self, msg: str):
        template = render_block(
            environment=environment,
            template_name=f'inventory/app/error.html',
            block_name='error',
            error=msg
        )
        await self.websocket.send_text(template)
    async def search_order_by_barcode(self, message: Message):
        order_adapter = self.env['order'].adapter
        order_list = await order_adapter.list(params={'search': message.barcode})
        orders = order_list['data']
        template = render_block(
            environment=environment,
            block_name='as_list',
            title='Search Orders',
            key=self.key,
            template_name='/inventory/app/orders.html',
            ui_key=f'order_type--{message.id}',
            lines=orders
        )
        return await self.websocket.send_text(template)

    async def suggest_scan_method(self, message: Message):
        adapter = self.websocket.scope['env']['move'].adapter
        move = await adapter.get(message.id)
        active_suggest = None
        for suggest in sorted(move['suggest_list_rel'], key=lambda x: x['priority']):
            if suggest['status'] != 'done':
                active_suggest = suggest
                break
        if active_suggest:
            message.id = active_suggest['id']#
            message.value = message.barcode
            return await self.action_suggest_done(message, barcode=message.barcode)
        else:
            return await self.send_error(f'No active suggestion')
    async def action_suggest_done(self, message: Message | dict, barcode: str = None):
        adapter = self.websocket.scope['env']['suggest'].adapter
        res: list = await adapter.action_suggest_confirm({
            'ids': [message.id],
            'value': message.value,
        })
        move = res[0]['move_id']
        if res[0]['status'] == 'done':
            move = await self.env['move'].adapter.get(res[0]['move_id'])
            suggests_not_done = [i for i in move['suggest_list_rel'] if i['status'] != 'done']
            if not suggests_not_done:
                return await self.get_moves_by_order_id(order_id=move['order_id'])
        return await self.get_move_card(move=move, barcode=barcode)

    async def action_order_start(self, message: Message):
        adapter = self.websocket.scope['env']['order'].adapter
        await adapter.order_start(payload={'ids': [message.id], 'user_id':self.user.user_id})
        return await self.get_moves_by_order_id(order_id=message.id)

    async def action_order_finish(self, message: Message):
        adapter = self.websocket.scope['env']['order'].adapter
        order = await adapter.assign_order(order_id=message.id, user_id=self.user.user_id)
        return await self.get_moves_by_order_id(order)

    async def get_move_card(self, move: dict | UUID4 | str, barcode: str = None):
        params = None
        if isinstance(move, uuid.UUID) or isinstance(move, str):
            move = await self.env['move'].adapter.get(move)

        product = await self.env['product'].adapter.get(move['product_id'])
        move['product'] = product
        locations = await self.env['location'].adapter.list(params={'id__in': [move['location_dest_id'], move['location_src_id']]})
        locations_map = {i['id']: i for i in locations['data']}
        move['location_dest'] = locations_map.get(move['location_dest_id'])
        move['location_src'] = locations_map.get(move['location_src_id'])
        active_suggest = None
        if barcode:
            # Если был сосканирован баркод
            in_product_suggest = [
                i for i in
                move['suggest_list_rel']
                if i['type'] == 'in_product' and i['status'] != 'done']
            if in_product_suggest:
                adapter = self.websocket.scope['env']['suggest'].adapter
                res = await adapter.action_suggest_confirm({
                    'ids': [in_product_suggest[0]['id']],
                    'value': barcode,
                })
                in_product_suggest[0]['status'] = res[0]['status']
                in_product_suggest[0]['result_value'] = res[0]['result_value']
        for suggest in sorted(move['suggest_list_rel'], key=lambda x: x['priority']):
            if suggest['status'] != 'done':
                active_suggest = suggest
                break
        template = render_block(
            environment=environment,
            template_name=f'inventory/app/move_card.html',
            block_name='as_card_processing',
            key=self.key,
            move=move,
            active_suggest=active_suggest,
        )
        return await self.websocket.send_text(template)

    async def search_move_by_barcode(self, message: Message):
        move_adapter = self.websocket.scope['env']['move'].adapter
        moves = await move_adapter.get_moves_by_barcode(barcode=message.barcode, order_id=message.id)
        if len(moves) > 1:
            ... # TODO: Если 2 ?
        elif len(moves) == 1:
            return await self.get_move_card(moves[0], message.barcode)
        else:
            ...

    def __init__(self, websocket: WebSocket, user: CurrentUser, key: str):
        self.key = key
        self.websocket = websocket
        self.user = user
        self.env = websocket.scope['env']

    def _render(self, block_name: str, title: str, template: str, ui_key: str, lines: list):
        return render_block(
            environment=environment,
            template_name=f'inventory/app/{template}.html',
            block_name=block_name,
            app=self,
            key=self.key,
            title=title,
            ui_key=ui_key,
            lines=lines,
        )

    async def go_to_last(self):
        """Отправляет юзер ана последнюю страницу или на главную если истории нет"""
        if self.history and len(self.history) > 1:
            self.history.pop(-1)
            await self.dispatch_message(self.history[-1], is_back=True)
        else:
            return await self.main_page()

    async def dispatch_message(self, message: dict | Message, is_back: bool = False):
        """Маршрутизирует сообщение """
        self.last_activity = datetime.now()
        if isinstance(message, dict):
            message = Message(**message)
        # if message.type != MessageType.BACK and not is_back:
        #     self.history.append(message)
        if message.type == MessageType.BACK:
            await self.go_to_last()
        elif message.type == MessageType.BARCODE:
            message.model, message.id, message.barcode = message.model_extra['scan-form-model'], \
                message.model_extra['scan-form-id'], message.model_extra['scan-form-barcode']
            scan_method = self.scan_methods.get(message.model)
            await getattr(self, scan_method)(message)
        elif message.type == MessageType.ACTION:
            action = self.actions.get(message.mode)
            await getattr(self, action)(message)

        elif message.type == MessageType.UPDATE:
            model_tempate = self.model_templates[message.model][message.mode]
            if message.model == 'order':
                order = await self.env['order'].adapter.get(message.id)
                template = render_block(
                    environment=environment,
                    template_name=f'inventory/app/{message.model}.html',
                    block_name=message.mode,
                    key=self.key,
                    order=order
                )
            return await self.websocket.send_text(template)
        else:
            if message.type != MessageType.BACK and not is_back:
                 self.history.append(message)

            next_page = self.pages.get(message.model)
            await getattr(self, next_page)(message)

    async def get_orders_by_order_type(self, order_type_id: UUID4 | str | Message):
        if isinstance(order_type_id, Message):
            order_type_id = order_type_id.id
        order_adapter = self.env['order'].adapter
        order_list = await order_adapter.list(params={
            'order_type_id__in': [order_type_id],
            'status__in': {'confirmed', 'assigned'}
        })
        orders = order_list['data']
        template = render_block(
            environment=environment,
            block_name='as_list',
            title='Orders',
            key=self.key,
            template_name='/inventory/app/orders.html',
            ui_key=f'order_type--{order_type_id}',
            orders=orders
        )
        return await self.websocket.send_text(template)

    async def get_moves_by_order_id(self, order_id: UUID4 | dict | Message):
        """Отдает список перемещений по типу"""
        if isinstance(order_id, dict):
            order = order_id
            moves = order_id['move_list_rel']

        elif isinstance(order_id, Message):
            moves_list = await self.env['move'].adapter.list(params={'order_id__in': [order_id.id]})
            order = await self.env['order'].adapter.get(order_id.id)
            moves = moves_list['data']
        else:
            moves_list = await self.env['move'].adapter.list(params={'order_id__in': [order_id]})
            order = await self.env['order'].adapter.get(order_id)
            moves = moves_list['data']
        products_list = await self.env['product'].adapter.list(
            params={
                'product_id__in': [i['product_id'] for i in moves]
            })
        products_map = {i['id']: i for i in products_list['data']}
        for move in moves:
            move['product'] = products_map.get(move['product_id'], None)
        template = render_block(
            environment=environment,
            template_name=f'inventory/app/moves.html',
            block_name='as_list',
            app=self,
            key=self.key,
            order=order,
            moves=moves,
        )
        return await self.websocket.send_text(template)

    async def main_page(self, message: dict = None):
        """ Отдает главную страницу c OrderType"""
        cls = await ClassView(
            self.websocket,
            'order_type',
            key=self.key,
            vars={
                'button_update': False,
                'button_view': True
            }
        )
        await cls.init()
        self.history = []
        return await self.websocket.send_text(cls.as_card_kanban)


task = None


@inventory_app.websocket("")
async def connect(websocket: WebSocket, user: Annotated[CurrentUser, Depends(get_token)]):
    """
            API получение сообщений
        """
    global kill_task
    if not user.user_id:  # type: ignore
        raise WebSocketException(code=status.HTTP_401_UNAUTHORIZED)
    try:
        app = users.get(user.user_id)  # type: ignore
        await websocket.accept()
        if not app:
            app = InventoryAPP(
                websocket=websocket,
                user=user,
                key=websocket.query_params.get('key')
            )
        else:
            app.websocket = websocket
            app.key = websocket.query_params.get('key')
        users[user.user_id] = app
        if kill_task is not None:
            if kill_task.done():
                kill_task = asyncio.create_task(kill_sessions(), name='kill_sessions')
        else:
            kill_task = asyncio.create_task(kill_sessions(), name='kill_sessions')
        await app.go_to_last()
        while True:
            message = await app.websocket.receive_json()
            try:
                await app.dispatch_message(message)
            except Exception as ex:
                print(traceback.format_exc())
                if len(app.history) > 1:
                    app.history.pop(-1)
                template = render_block(
                    environment=environment,
                    template_name=f'inventory/app/error.html',
                    block_name='error',
                    error=f'{ex.detail["code"]} - {ex.detail["msg"]}'
                )
                await app.websocket.send_text(template)
    except WebSocketDisconnect as ex:
        raise WebSocketDisconnect

    except Exception as ex:
        raise WebSocketDisconnect


async def dispatch_message(message: dict):
    if message['HEADERS']['HX-Trigger'] == 'barcode':
        a = 1
