from collections import defaultdict
from lib2to3.fixes.fix_input import context
from uuid import UUID

from attr.filters import exclude
from fastapi import APIRouter, Depends
from fastapi import Request
from fastapi.responses import HTMLResponse

from app.front.apps.inventory.views import OrderView, StoreStaffView, OrderTypeView
from app.front.template_spec import templates
from app.front.utills import BasePermit, render
from core.frontend.constructor import ClassView

inventory = APIRouter()


class OrderPermit(BasePermit):
    permits = ['order_list']

class Temp:
    def __init__(self, request: Request, template=None):
        self.request = request

    async def __call__(self):
        return self.request

@inventory.get("/dashboard", response_class=HTMLResponse, dependencies=[Depends(OrderPermit)])
async def order(request: Request):
    """Список складских ордеров"""
    template = f'widgets/list{"" if request.scope["htmx"].hx_request else "-full"}.html'
    cls = OrderView(request)
    render(request, template, context={'cls': cls})


@inventory.get("/store_monitor", response_class=HTMLResponse)
async def store_monitor(orders: OrderView = Depends(), order_type: OrderTypeView = Depends()):
    """Интерфейс работы со своим складом"""
    store_staff_model = orders.r.scope['env']['store_staff']
    orders._exclude = ['store_id']
    async with store_staff_model.adapter as a:
        data = await a.list(params={'user_id': orders.r.user.user_id})
        if not data['data']:
            return render(orders.r, 'inventory/user_not_attached_store.html')
        store_staff = data['data'][0]
        store_staff_cls = StoreStaffView(orders.r)
        await store_staff_cls.init(params={'store_id': store_staff['store_id']})
    return render(
        orders.r, 'inventory/store_monitor/store_monitor.html',
        context={'store_staff_cls': store_staff_cls, 'order_type': order_type, 'orders': orders}
    )


@inventory.get("/store_monitor_orders", response_class=HTMLResponse)
async def store_monitor_otders(orders: OrderView = Depends(), order_types: OrderTypeView = Depends()):
    """Интерфейс работы со своим складом"""
    await orders.init(exclude=['store_id'])
    orders.v.update = False
    order_types_map = defaultdict(list)
    for order in orders:
        order_types.append(order.order_type_rel.val)
    for order in orders:
        order_types_map[order.order_type_rel.val].append(order)
    return render(orders.r, 'inventory/store_monitor/store_monitor_orders.html',
        context={'order_types_map': order_types_map}
    )
@inventory.get("/store_monitor/line", response_class=HTMLResponse)
async def store_monitor_line(order_id: UUID, order_view: OrderView = Depends()):
    """Отдает лайну для монитора склада"""
    order = await order_view.get_lines(ids=[order_id])
    return render(order_view.r, 'inventory/store_monitor/store_monitor_order_line.html', context={'order': order})

@inventory.get("/store_monitor/order_detail", response_class=HTMLResponse)
async def store_monitor_line(order_id: UUID, order_view: OrderView = Depends()):
    """Отдает лайну для монитора склада"""
    order = await order_view.get_lines(ids=[order_id])
    return render(order_view.r, 'inventory/store_monitor/store_monitor_order_detail.html', context={'order': order})
