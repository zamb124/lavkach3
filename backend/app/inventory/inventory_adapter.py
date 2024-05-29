import json
from uuid import UUID

from app.inventory.inventory_config import config
from core.fastapi.adapters import BaseAdapter


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

    async def action_move_confirm(self, payload: dict | str):
        ""
        path = f'/api/inventory/move/confirm'
        if isinstance(payload, str):
            payload = json.loads(payload)
        responce = await self.client.post(self.host + path, json=payload, params={})
        return responce.json()

