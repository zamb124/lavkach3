import httpx
from httpx import QueryParams

from app.bff.bff_config import config
from fastapi import Request


class InventoryAdapter:
    headers: dict
    session: httpx.AsyncClient = None
    inventory_url: str = f"http://{config.services['inventory']['DOMAIN']}:{config.services['inventory']['PORT']}"
    order_list_path = '/api/inventory/order'
    def __init__(self, request: Request):
        self.headers = {'Authorization': request.headers.get('Authorization') or request.cookies.get('token')}

    async def __aenter__(self):
        self.session = httpx.AsyncClient(headers=self.headers)
        return self

    async def __aexit__(self, *args, **kwargs):
        await self.session.aclose()

    async def get_orders(self, params=None, **kwargs):
        responce = await self.session.get(self.inventory_url + self.order_list_path, params=params)
        data = responce.json()
        return data

    async def order(self, params=None, **kwargs):
        responce = await self.session.get(self.inventory_url + self.order_list_path, params=params)
        data = responce.json()
        return data

    async def get_order_types(self, params=None, **kwargs):
        path = '/api/inventory/order_type'
        responce = await self.session.get(self.inventory_url + path, params=params)
        data = responce.json()
        return data

