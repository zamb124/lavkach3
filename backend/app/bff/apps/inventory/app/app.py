import asyncio
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Annotated, Optional

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
from core.fastapi.frontend.constructor import ClassView
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

async  def kill_sessions():
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


    async def search_order_by_barcode(self, message: Message):
        cls = await ClassView(
            self.websocket, 'order',
            key=self.key,
            params={'search': message.barcode},
            force_init=True
        )
        template = self._render(
            block_name='as_list',
            title='Search Orders',
            template='orders',
            ui_key=f'order_type--{message.id}',
            lines=cls.lines.lines
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
            await self.action_suggest_done(message)
    async def action_suggest_done(self, message: Message| dict):
        adapter = self.websocket.scope['env']['suggest'].adapter
        res = await adapter.action_suggest_confirm({
            'ids': [message.id],
            'value': message.value,
        })
        return self.get_move_card(res['move_id'])

    async def action_order_start(self, message: Message):
        adapter = self.websocket.scope['env']['order'].adapter
        order = await adapter.assign_order(order_id=message.id, user_id=self.user.user_id)
        return await self.get_moves_by_order_id(message)

    async def get_move_card(self, move: dict | UUID4 | str):
        params = None
        if isinstance(move, uuid.UUID) or isinstance(move, str):
            params = {'id__in': [move]}
            data = None
        else:
            data = [move]
        cls = await ClassView(
            self.websocket, 'move',
            key=self.key,
            params=params,
            join_fields=['product_id', 'location_dest_id', 'location_src_id'],
            force_init=False
        )
        await cls.init(data=data)
        if len(cls.lines.lines) > 1:
            return await self.websocket.send_text(cls.as_card_kanban)
        else:
            line = cls.lines.lines[0]
            active_suggest = None
            for suggest in sorted(line.fields.suggest_list_rel.val, key=lambda x: x['priority']):
                if suggest['status'] != 'done':
                    active_suggest = suggest
                    break
            template = render_block(
                environment=environment,
                template_name=f'inventory/app/move_card.html',
                block_name='as_card_processing',
                key=self.key,
                title=line.display_title,
                ui_key=line.ui_key,
                line=line,
                active_suggest=active_suggest,
            )
            return await self.websocket.send_text(template)
    async def search_move_by_barcode(self, message: Message):
        move_adapter = self.websocket.scope['env']['move'].adapter
        moves = await move_adapter.get_moves_by_barcode(barcode=message.barcode,  order_id=message.id)
        return await self.get_move_card(moves[0])
    def __init__(self, websocket: WebSocket, user: CurrentUser, key: str):
        self.key = key
        self.websocket = websocket
        self.user = user

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
        if message.type != MessageType.BACK and not is_back:
            self.history.append(message)
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
            cls = await ClassView(
                self.websocket, message.model,
                key=self.key,
                params={'id__in': message.id},
                force_init=True
            )
            line = cls.lines.lines[0]
            template = render_block(
                environment=environment,
                template_name=f'inventory/app/{message.model}.html',
                block_name=message.mode,
                key=line.key,
                title=line.display_title,
                ui_key=line.ui_key,
                line=line,
            )
            return await self.websocket.send_text(template)
        else:
            next_page = self.pages.get(message.model)
            await getattr(self, next_page)(message)
        ...

    async def get_orders_by_order_type(self, message: Message):
        """Отдает список перемещений по типу"""
        cls = await ClassView(
            self.websocket, 'order',
            key=self.key,
            params={'order_type_id__in': [message.id], 'store_id__in': [self.user.store_id]},
            vars={
                'button_update': False,
                'button_view': True
            },
            force_init=True
        )
        template = self._render(
            block_name='as_list',
            title='List Orders',
            template='orders',
            ui_key=f'order_type--{message.id}',
            lines=cls.lines.lines
        )
        return await self.websocket.send_text(template)

    async def get_moves_by_order_id(self, message: Message):
        """Отдает список перемещений по типу"""
        move_cls = await ClassView(
            self.websocket, 'move',
            key=self.key,
            params={'order_id__in': [message.id]},
            join_fields=['product_id'],              # Нам нуно достать product_id ради ссылки на картинку
            vars={
                'button_update': False,
                'button_view': True
            },
        )
        move_cls_task = asyncio.create_task(move_cls.init())
        order_cls = await ClassView(
            self.websocket, 'order',
            key=self.key,
            params={'id__in': [message.id]},
            vars={
                'button_update': False,
                'button_view': True
            },
            force_init=True
        )
        order_cls_task = asyncio.create_task(order_cls.init())
        await asyncio.gather(move_cls_task, order_cls_task)
        template = render_block(
            environment=environment,
            template_name=f'inventory/app/moves.html',
            block_name='as_list',
            app=self,
            key=self.key,
            order=order_cls.lines.lines[0],
            moves=move_cls.lines.lines,
        )
        return await self.websocket.send_text(template)

    async def main_page(self, message: dict = None):
        """ Отдает главную страницу c OrderType"""
        cls = await ClassView(
            self.websocket, 'order_type',
            key=self.key,
            vars={
                'button_update': False,
                'button_view': True
            }
        )
        await cls.init()
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
                kill_task = asyncio.create_task(kill_sessions(),  name='kill_sessions')
        else:
            kill_task = asyncio.create_task(kill_sessions(),  name='kill_sessions')
        await app.go_to_last()
        while True:
            message = await app.websocket.receive_json()
            await app.dispatch_message(message)


    except WebSocketDisconnect as ex:
        raise WebSocketDisconnect

    except Exception as ex:
        raise WebSocketDisconnect


async def dispatch_message(message: dict):
    if message['HEADERS']['HX-Trigger'] == 'barcode':
        a = 1
