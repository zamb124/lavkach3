from fastapi import APIRouter, Depends
from fastapi import Request
from fastapi.responses import HTMLResponse

from app.front.apps.inventory.views import StoreView
from app.front.template_spec import templates
from app.front.utills import BasePermit
from core.frontend.constructor import ClassView

store_router = APIRouter()


@store_router.get("", response_class=HTMLResponse)
async def store(cls: StoreView = Depends()):
    """Список складских ордеров"""
    template = f'widgets/list{"" if cls.r.scope["htmx"].hx_request else "-full"}.html'
    return templates.TemplateResponse(cls.r, template, context={'cls': cls})



