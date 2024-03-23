from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from fastapi_htmx import htmx

from app.bff.dff_helpers.htmx_decorator import s
from core.fastapi.adapters.base_adapter import Request

order_router = APIRouter()

@order_router.get("", response_class=HTMLResponse)
@htmx(*s('inventory/order/order'))
async def company(request: Request):
    return {}

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
    async with request.scope['env'].inventory as oa:
        orders_data = await oa.list(model='order', params=request.query_params) # Достаю сначала ордера
    async with request.scope['env'].basic as ba:
        stores_data = await ba.list(model='store') # Теперь склады
        # Склеиваю
    for order in orders_data['data']:
        for store in stores_data['data']:
            if order['store_id'] == store['id']:
                order.update({'store': store})
        order['status_badge'] = status_badges_map[order['status']]
    return orders_data
