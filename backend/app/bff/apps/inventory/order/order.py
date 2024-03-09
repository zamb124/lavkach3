import asyncio
import uuid
from asyncio import sleep
from typing import Optional

import aiohttp
import httpx
from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi_htmx import htmx, htmx_init
from starlette.responses import Response
from starlette.status import HTTP_200_OK
from starlette.templating import Jinja2Templates
from app.bff.bff_config import config

from app.bff.dff_helpers.htmx_decorator import s
from app.bff.template_spec import templates
from app.inventory.order.models import OrderStatus

order_router = APIRouter()


class OrderAdapter:
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

    async def get_orders(self, params, **kwargs):
        responce = await self.session.get(self.inventory_url + self.order_list_path, params=params)

        data = await responce.json()
        return data

    async def get_company(self, company_id: uuid.UUID):
        async with self.session.get(self.basic_url + self.path +f'/{company_id.__str__()}') as resp:
            data = await resp.json()
        return data

@order_router.get("", response_class=HTMLResponse)
@htmx(*s('inventory/order/order'))
async def company(request: Request):

    a = OrderStatus.DONE
    return {'statuses': OrderStatus, 'orders': {}}

@order_router.get("/table", response_class=HTMLResponse)
@htmx(*s('inventory/order/order-table'))
async def company_list(request: Request):
    async with OrderAdapter(request) as oa:
        data = await oa.get_orders(request.query_params)
    return {
        'companies': data['data']
    }
