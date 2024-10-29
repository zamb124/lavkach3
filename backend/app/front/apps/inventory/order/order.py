from fastapi import APIRouter, Depends
from fastapi import Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from urllib3 import request

from app.front.template_spec import templates
from app.front.utills import BasePermit, BaseClass
from core.frontend.constructor import ClassView, get_view, BaseSchema
from core.permissions import permits

order_router = APIRouter()




class OrderView(ClassView):
    """Переопределяем модель"""
    def __init__(self, request: Request, schema: BaseSchema = None):
        super().__init__(request=request, model='order', permits=permits)


@order_router.get("", response_class=HTMLResponse)
async def order(request: Request, view: OrderView = Depends()):
    """Список складских ордеров"""
    template = f'widgets/list{"" if request.scope["htmx"].hx_request else "-full"}.html'
    return templates.TemplateResponse(request, template, context={'cls': view})


@order_router.get("/mystore", response_class=HTMLResponse)
async def mystore(request: Request):
    """Интерфейс работы со своим складом"""
    template = f'widgets/list{"" if request.scope["htmx"].hx_request else "-full"}.html'
    order_cls = await OrderView(request)
    store_dash = order_cls.get_store_dashboard()
    return templates.TemplateResponse(request, template, context={'cls': cls})
