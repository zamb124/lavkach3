from fastapi import APIRouter, Depends
from fastapi import Request
from fastapi.responses import HTMLResponse

from app.bff.template_spec import templates
from app.bff.utills import BasePermit
from core.frontend.constructor import ClassView

order_type_router = APIRouter()

class OrderTypePermit(BasePermit):
    permits = ['order_type_list']


@order_type_router.get("", response_class=HTMLResponse, dependencies=[Depends(OrderTypePermit)])
async def order_type(request: Request):
    """Список типов складских ордеров"""
    cls = ClassView(request,  'order_type')
    template = f'widgets/list{"" if request.scope["htmx"].hx_request else "-full"}.html'
    return templates.TemplateResponse(request, template, context={'cls': cls})
