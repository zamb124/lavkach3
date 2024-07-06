from fastapi import APIRouter, Depends
from fastapi import Request
from fastapi.responses import HTMLResponse

from app.bff.template_spec import templates
from app.bff.utills import BasePermit
from core.fastapi.frontend.constructor import ClassView

order_router = APIRouter()


class OrderView(ClassView):
    """Переопределяем модель"""
    model_name = "order"

class OrderPermit(BasePermit):
    permits = ['order_list']

@order_router.get("", response_class=HTMLResponse, dependencies=[Depends(OrderPermit)])
async def order(request: Request):
    """Список складских ордеров"""
    template = f'widgets/list{"" if request.scope["htmx"].hx_request else "-full"}.html'
    cls = await OrderView(request)
    return templates.TemplateResponse(request, template, context={'cls': cls})


@order_router.get("/mystore", response_class=HTMLResponse)
async def mystore(request: Request):
    """Интерфейс работы со своим складом"""
    template = f'widgets/list{"" if request.scope["htmx"].hx_request else "-full"}.html'
    order_cls = await OrderView(request)
    store_dash = order_cls.get_store_dashboard()
    return templates.TemplateResponse(request, template, context={'cls': cls})
