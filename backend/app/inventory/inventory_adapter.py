import json
from uuid import UUID

from app.inventory.inventory_config import config
from app.inventory.order.schemas import SuggestConfirmScheme
from app.inventory.order.schemas.order_schemas import AssignUser
from app.inventory.schemas import CreateMovements
from core.fastapi.adapters import BaseAdapter
from core.fastapi.adapters.action_decorator import action
from core.types import UUIDEncoder


class InventoryAdapter(BaseAdapter):
    module = 'inventory'
    protocol = config.APP_PROTOCOL
    port = config.APP_PORT
    host = config.APP_HOST


    async def order(self, params=None, **kwargs):
        data = await self.list(model='order', params=params)
        return data

    async def order_type(self, params=None, **kwargs):
        path = '/api/inventory/order_type'
        responce = await self.session.get(self.domain + path, params=params)
        data = responce.json()
        return data

    @action(model='move', multiple=False, permits=[])
    async def action_move_confirm(self, payload: dict | str) -> dict:
        """

        """
        path = f'/api/inventory/move/confirm'
        if isinstance(payload, str):
            payload = json.loads(payload)
        responce = await self.client.post(self.host + path, json=payload, params={})
        return responce.json()

    @action(model='move', multiple=False, permits=[])
    async def action_move_confirmmmm(self, payload: dict | str):
        """

        """
        path = f'/api/inventory/move/confirm'
        if isinstance(payload, str):
            payload = json.loads(payload)
        responce = await self.client.post(self.host + path, json=payload, params={})
        return responce.json()

    @action(model='suggest',schema=SuggestConfirmScheme, multiple=True, permits=[])
    async def action_suggest_confirm(self, schema: SuggestConfirmScheme | dict):
        """Подтверждение саджеста, введите то значение, которое бы отсканировал пользователь"""
        if isinstance(schema, dict):
            schema = SuggestConfirmScheme(**schema)
        path = f'/api/inventory/suggest/confirm'
        responce = await self.client.post(self.host + path, json=schema.model_dump_json(), params={})
        return responce.json()

    @action(model='move', multiple=False, permits=[])
    async def get_moves_by_barcode(self, barcode: str, order_id: UUID):
        path = f'/api/inventory/move/get_moves_by_barcode'
        payload = {
            'barcode': barcode,
            'order_id': order_id.__str__()
        }
        responce = await self.client.post(self.host + path, json=payload, params={})
        return responce.json()

    @action(model='order', multiple=False, permits=[])
    async def order_confirm(self, payload: dict, **kwargs):
        """Подтверждает ордер и резервирует мувы"""
        if isinstance(payload, dict):
            payload = json.dumps(payload, cls=UUIDEncoder)
        path = f'/api/inventory/order/order_confirm'
        responce = await self.client.post(self.host + path, json=payload, params={})
        return responce.json()

    @action(model='order', multiple=False, permits=[])
    async def order_start(self, payload: dict, **kwargs):
        """Переводит ордер из CONFIRMED в WAITING"""
        if isinstance(payload, dict):
            payload = json.dumps(payload, cls=UUIDEncoder)
        path = f'/api/inventory/order/order_start'
        responce = await self.client.post(self.host + path, json=payload, params={})
        return responce.json()

    @action(model='order', schema=AssignUser, multiple=False, permits=[])
    async def order_assign(self, schema: AssignUser):
        """Назначение пользователя на заказ, если не указан, то возьется из запроса"""

        schema_body = schema.model_dump_json()
        path = f'/api/inventory/order/order_assign'
        responce = await self.client.post(self.host + path, json=schema_body, params={})
        return responce.json()

    @action(model='order', multiple=False, permits=[])
    async def order_complete(self, payload: dict, **kwargs):
        """Переводит ордер из CONFIRMED в WAITING"""
        path = f'/api/inventory/order/order_complete'
        responce = await self.client.post(self.host + path, json=payload, params={})
        return responce.json()

    @action(model='order', schema=CreateMovements, multiple=False, permits=[])
    async def create_movements(self, payload: dict, **kwargs):
        """Переводит ордер из CONFIRMED в WAITING"""
        if isinstance(payload, dict):
            payload = json.dumps(payload, cls=UUIDEncoder)
        path = f'/api/inventory/create_movements'
        responce = await self.client.post(self.host + path, json=payload, params={})
        return responce.json()