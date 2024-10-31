from fastapi import APIRouter, Depends
from fastapi import Request
from fastapi.responses import HTMLResponse

from app.front.apps.inventory.views import OrderView
from app.front.template_spec import templates

order_router = APIRouter()


@order_router.get("", response_class=HTMLResponse)
async def order(request: Request, view: OrderView = Depends()):
    """Список складских ордеров"""
    template = f'widgets/list{"" if request.scope["htmx"].hx_request else "-full"}.html'
    return templates.TemplateResponse(request, template, context={'cls': view})
