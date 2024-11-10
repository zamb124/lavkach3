from fastapi import Depends, APIRouter
from fastapi import Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from app.front.apps.inventory.order.order_create.schemas import OrderCreateView, Product
from app.front.utills import render
from core.frontend.constructor import ClassView
from core.frontend.utils import clean_filter

order_create_router = APIRouter()


class Schema(BaseModel):
    key: str

    class Config:
        extra = 'allow'


@order_create_router.get("", response_class=HTMLResponse)
async def order_create(request: Request, order: OrderCreateView = Depends(), store_id: str = None):
    order.store_id.val = store_id
    return render(request, 'inventory/order/order_create/order_create.html', context={'order': order})


@order_create_router.post("", response_class=HTMLResponse)
async def order_create(request: Request, schema: Schema):
    data = clean_filter(schema.model_extra, schema.key)
    return render(request, 'inventory/order/order_create/order_create.html', context={'order': order})


@order_create_router.get("/add_product", response_class=HTMLResponse)
async def order_add_product(request: Request, key: str = None):
    product = ClassView(request=request, model=Product, key=key)
    return render(
        request, 'inventory/order/order_create/order_create_products_line.html',
        context={'product': product}
    )
