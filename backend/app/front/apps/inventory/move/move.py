from fastapi import APIRouter, Depends
from fastapi import Request
from fastapi.responses import HTMLResponse

from app.front.apps.inventory.views import MoveView
from app.front.template_spec import templates

move_router = APIRouter()

@move_router.get("", response_class=HTMLResponse)
async def move(cls: MoveView = Depends()):
    """Список перемещений"""
    template = f'widgets/list{"" if cls.r.scope["htmx"].hx_request else "-full"}.html'
    return templates.TemplateResponse(cls.r, template, context={'cls': cls})



@move_router.get("/kanban", response_class=HTMLResponse)
async def move(request: Request):
    """
        kanban custom view
    """
    cls = MoveView(request)
    view = await cls._get_table()
    template = f'inventory/move/move_list{"" if request.scope["htmx"].hx_request else "-full"}.html'
    return templates.TemplateResponse(request, template, context={'view': view})
