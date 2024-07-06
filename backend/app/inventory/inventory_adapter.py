import json

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
    async def action_suggest_confirm(self, schema: SuggestConfirmScheme):
        path = f'/api/inventory/suggest/confirm'
        responce = await self.client.post(self.host + path, json=schema.model_dump_json(), params={})
        return responce.json()
