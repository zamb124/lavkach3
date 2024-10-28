from fastapi import APIRouter, Depends
from fastapi import Request
from fastapi.responses import HTMLResponse

from app.front.template_spec import templates
from app.front.utills import BasePermit
from core.frontend.constructor import ClassView

inventory = APIRouter()


class OrderView(ClassView):
    """Переопределяем модель"""
    model_name = "order"

class OrderPermit(BasePermit):
    permits = ['order_list']

@inventory.get("/dashboard", response_class=HTMLResponse, dependencies=[Depends(OrderPermit)])
async def order(request: Request):
    """Список складских ордеров"""
    template = f'widgets/list{"" if request.scope["htmx"].hx_request else "-full"}.html'
    cls = OrderView(request)
    return templates.TemplateResponse(request, template, context={'cls': cls})


@inventory.get("/store_monitor", response_class=HTMLResponse)
async def mystore(request: Request):
    """Интерфейс работы со своим складом"""
    template = f'widgets/list{"" if request.scope["htmx"].hx_request else "-full"}.html'
    store_cls = await StoreView(request)
    store_dash = store_cls.get_store_dashboard()
    return templates.TemplateResponse(request, template, context={'cls': cls})