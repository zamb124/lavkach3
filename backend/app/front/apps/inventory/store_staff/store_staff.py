from fastapi import APIRouter, Depends
from fastapi import Request
from fastapi.responses import HTMLResponse

from app.front.apps.inventory.views import MoveView, StoreStaffView
from app.front.template_spec import templates

store_staff_router = APIRouter()

@store_staff_router.get("", response_class=HTMLResponse)
async def store_staff(cls: StoreStaffView = Depends()):
    """Список перемещений"""
    template = f'widgets/list{"" if cls.r.scope["htmx"].hx_request else "-full"}.html'
    return templates.TemplateResponse(cls.r, template, context={'cls': cls})