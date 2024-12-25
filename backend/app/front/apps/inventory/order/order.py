from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi import Request
from fastapi.responses import HTMLResponse

from app.front.apps.inventory.views import OrderView
from app.front.template_spec import templates
from app.front.utills import render

order_router = APIRouter()

@order_router.get("", response_class=HTMLResponse)
async def order(request: Request, view: OrderView = Depends()):
    """Список складских ордеров"""
    template = f'widgets/list.html'
    return await render(
        request=request,
        template=template,
        context={'cls': view}
    )


@order_router.get("/line", response_class=HTMLResponse)
async def order_line(order_id: UUID, order_view: OrderView = Depends()):
    """Отдает лайну для монитора склада"""
    order = await order_view.get_lines(ids=[order_id])
    return await render(
        request=order_view.r,
        template='inventory/order/order_line.html',
        context={'order': order}
    )


@order_router.get("/detail", response_class=HTMLResponse)
async def order_detail(order_id: UUID, order_view: OrderView = Depends()):
    """Отдает лайну для монитора склада"""
    order = await order_view.get_lines(ids=[order_id])
    return await render(
        request=order_view.r,
        template='inventory/order/order_detail.html',
        context={'order': order}
    )
