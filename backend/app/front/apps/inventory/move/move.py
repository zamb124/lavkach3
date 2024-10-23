from fastapi import APIRouter, Depends
from fastapi import Request
from fastapi.responses import HTMLResponse

from app.front.template_spec import templates
from app.front.utills import BasePermit
from core.frontend.constructor import ClassView

move_router = APIRouter()
class MoveView(ClassView):
    """Переопределяем модель"""
    model_name = "move"


class MovePermit(BasePermit):
    permits = ['move_list']

@move_router.get("", response_class=HTMLResponse, dependencies=[Depends(MovePermit)])
async def move(request: Request):
    """Список перемещений"""
    cls = MoveView(request)
    template = f'widgets/list{"" if request.scope["htmx"].hx_request else "-full"}.html'
    return templates.TemplateResponse(request, template, context={'cls': cls})



@move_router.get("/kanban", response_class=HTMLResponse)
async def move(request: Request):
    """
        kanban custom view
    """
    cls = MoveView(request)
    view = await cls._get_table()
    template = f'inventory/move/move_list{"" if request.scope["htmx"].hx_request else "-full"}.html'
    return templates.TemplateResponse(request, template, context={'view': view})
