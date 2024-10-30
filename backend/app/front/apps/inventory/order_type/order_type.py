from fastapi import APIRouter, Depends
from fastapi import Request
from fastapi.responses import HTMLResponse

from app.front.apps.inventory.views import OrderTypeView
from app.front.template_spec import templates
from app.front.utills import BasePermit
from core.frontend.constructor import ClassView, BaseSchema

order_type_router = APIRouter()





@order_type_router.get("", response_class=HTMLResponse)
async def order_type(cls: OrderTypeView = Depends()):
    """Список типов складских ордеров"""
    template = f'widgets/list{"" if cls.r.scope["htmx"].hx_request else "-full"}.html'
    return templates.TemplateResponse(cls.r, template, context={'cls': cls})
