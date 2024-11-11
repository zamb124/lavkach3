from collections import defaultdict
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from starlette.requests import Request
from starlette.responses import HTMLResponse

from app.front.apps.inventory.views import OrderView, OrderTypeView, StoreStaffView
from app.front.utills import render
from app.inventory.schemas import CreateMovements, Product, Package
from core.frontend.constructor import ClassView, BaseSchema
from core.frontend.utils import clean_filter

store_monitor_router = APIRouter()

class CreateMovementsView(ClassView):
    """Переопределяем модель"""
    def __init__(self, request: Request, schema: BaseSchema = None):
        permits = ['order_list']
        super().__init__(request=request, model=CreateMovements, schema=schema, permits=permits)


@store_monitor_router.get("", response_class=HTMLResponse)
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


@store_monitor_router.get("/orders", response_class=HTMLResponse)
async def store_monitor_otders(orders: OrderView = Depends(), order_types: OrderTypeView = Depends(),
                               store_id: UUID = None):
    """Интерфейс работы со своим складом"""
    await orders.init(params={'store_id__in': [store_id]}, exclude=['store_id'])
    orders.v.update = False
    order_types_map = defaultdict(list)
    for order in orders:
        order_types.append(order.order_type_rel.val)
    for order in orders:
        order_types_map[order.order_type_rel.val].append(order)
    return render(
        orders.r, 'inventory/store_monitor/store_monitor_orders.html',
        context={'order_types_map': order_types_map, 'store_id': store_id},
    )


class Schema(BaseModel):
    key: str

    class Config:
        extra = 'allow'


@store_monitor_router.get("/create_movements", response_class=HTMLResponse)
async def create_movements(request: Request, order: CreateMovementsView = Depends(), store_id: str = None):
    order.store_id.val = store_id
    return render(request, 'inventory/store_monitor/create_movements/create_movements.html', context={'order': order})


@store_monitor_router.post("/create_movements", response_class=HTMLResponse)
async def create_movements(request: Request, schema: Schema):
    order = OrderView(request)
    data = clean_filter(schema.model_extra, schema.key)
    async with order.v.model.adapter as a:
        order = await a.create_movements(data[0])
    return render(order.r, 'inventory/store_monitor/create_movements/create_movements.html', context={'order': order})


@store_monitor_router.get("/create_movements/add_product", response_class=HTMLResponse)
async def create_movements_add_product(request: Request, key: str = None):
    product = ClassView(request=request, model=Product, key=key)
    return render(
        request, 'inventory/store_monitor/create_movements/create_movements_product_line.html',
        context={'product': product}
    )

@store_monitor_router.get("/create_movements/add_package", response_class=HTMLResponse)
async def create_movements_add_product(request: Request, key: str = None):
    package = ClassView(request=request, model=Package, key=key)
    return render(
        request, 'inventory/store_monitor/create_movements/create_movements_package_line.html',
        context={'package': package}
    )