import json
from uuid import UUID

from app.inventory.inventory_config import config
from app.inventory.order.schemas import SuggestConfirmScheme
from core.fastapi.adapters import BaseAdapter
from core.fastapi.adapters.action_decorator import action


class InventoryAdapter(BaseAdapter):
    module = 'basic'
    protocol = config.APP_PROTOCOL
    port = config.APP_PORT
    host = config.APP_HOST
    bff_methods = []

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
    async def order_start(self, order_id, user_id: UUID):
        """Назначение пользователя на заказ, если не указан, то возьется из запроса"""
        if isinstance(user_id, UUID):
            user_id = user_id.__str__()
        if isinstance(order_id, UUID):
            order_id = order_id.__str__()
        path = f'/api/inventory/order/order_start'
        payload = {
            'order_id': order_id,
            'user_id': user_id if user_id else None
        }
        responce = await self.client.post(self.host + path, json=payload, params={})
        return responce.json()

    @action(model='order', multiple=False, permits=[])
    async def assign_order(self, order_id, user_id: UUID):
        """Назначение пользователя на заказ, если не указан, то возьется из запроса"""
        if isinstance(user_id, UUID):
            user_id = user_id.__str__()
        if isinstance(order_id, UUID):
            order_id = order_id.__str__()
        path = f'/api/inventory/order/assign_order'
        payload = {
            'order_id': order_id,
            'user_id': user_id if user_id else None
        }
        responce = await self.client.post(self.host + path, json=payload, params={})
        return responce.json()