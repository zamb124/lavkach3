import asyncio
import uuid
from asyncio import sleep
from typing import Optional

import aiohttp
import httpx
from fastapi import APIRouter, Query
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi_htmx import htmx, htmx_init
from starlette.responses import Response
from starlette.status import HTTP_200_OK
from starlette.templating import Jinja2Templates

from app.bff.adapters import InventoryAdapter, BasicAdapter
from app.bff.bff_config import config

from app.bff.dff_helpers.htmx_decorator import s
from app.bff.template_spec import templates
from app.inventory.order.models import OrderStatus
from datetime import datetime, timedelta

order_router = APIRouter()

@order_router.get("", response_class=HTMLResponse)
@htmx(*s('inventory/order/order'))
async def company(request: Request):

    a = OrderStatus.DONE
    return {'statuses': OrderStatus, 'orders': {}}

status_badges_map = {
    'assigned': 'info',
    'canceled': 'danger',
    'confirmed': 'primary',
    'done': 'success',
    'draft': 'dark',
    'waiting': 'secondary'
}
@order_router.get("/table", response_class=HTMLResponse)
@htmx(*s('inventory/order/order-table'))
async def order_list(request: Request,):
    async with InventoryAdapter(request) as oa:
        # Достаю сначала ордера
        orders_data = await oa.get_orders(request.query_params)
    async with InventoryAdapter(request) as oa:
        # Достаю все типы ордеров
        order_types_data = await oa.get_order_types()
    async with BasicAdapter(request) as oa:
        # Теперь склады
        stores_data = await oa.get_stores()
        # Склеиваю
    a=1
    for order in orders_data['data']:
        for store in stores_data['data']:
            if order['store_id'] == store['id']:
                order.update({'store': store})
        order['status_badge'] = status_badges_map[order['status']]
    return {
        'orders': orders_data['data'],
        'search': request.query_params.get('search'),
        'stores': stores_data.get('data'),
        'order_types': order_types_data.get('data'),
    }
