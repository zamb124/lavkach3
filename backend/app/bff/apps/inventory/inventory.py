from fastapi import APIRouter, Depends
from fastapi import Request
from fastapi.responses import HTMLResponse

from app.bff.template_spec import templates
from app.bff.utills import BasePermit
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
    cls = await OrderView(request)
    return templates.TemplateResponse(request, template, context={'cls': cls})
