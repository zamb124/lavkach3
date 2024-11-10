from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi import Request
from fastapi.responses import HTMLResponse

from app.front.apps.inventory.order.order_create.order_create import order_create_router
from app.front.apps.inventory.views import OrderView
from app.front.template_spec import templates
from app.front.utills import render

order_router = APIRouter()
order_router.include_router(order_create_router, prefix="/create", tags=["order"])

@order_router.get("", response_class=HTMLResponse)
async def order(request: Request, view: OrderView = Depends()):
    """Список складских ордеров"""
    template = f'widgets/list{"" if request.scope["htmx"].hx_request else "-full"}.html'
    return templates.TemplateResponse(request, template, context={'cls': view})


@order_router.get("/line", response_class=HTMLResponse)
async def order_line(order_id: UUID, order_view: OrderView = Depends()):
    """Отдает лайну для монитора склада"""
    order = await order_view.get_lines(ids=[order_id])
    return render(order_view.r, 'inventory/order/order_line.html', context={'order': order})


@order_router.get("/detail", response_class=HTMLResponse)
async def order_detail(order_id: UUID, order_view: OrderView = Depends()):
    """Отдает лайну для монитора склада"""
    order = await order_view.get_lines(ids=[order_id])
    return render(order_view.r, 'inventory/order/order_detail.html', context={'order': order})
