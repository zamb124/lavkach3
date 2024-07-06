from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import HTMLResponse

from app.bff.utills import BasePermit
from core.fastapi.frontend.schema_recognizer import ClassView
from app.bff.template_spec import templates
from fastapi import APIRouter, Depends
move_router = APIRouter()

class MovePermit(BasePermit):
    permits = ['move_list']

@move_router.get("", response_class=HTMLResponse, dependencies=[Depends(MovePermit)])
async def move(request: Request):
    """Список перемещений"""
    cls = await ClassView(request, 'move')
    template = f'widgets/list{"" if request.scope["htmx"].hx_request else "-full"}.html'
    return templates.TemplateResponse(request, template, context={'cls': cls})



@move_router.get("/kanban", response_class=HTMLResponse)
async def move(request: Request):
    """
        kanban custom view
    """
    cls = ClassView(request, 'move')
    view = await cls._get_table()
    template = f'inventory/move/move_list{"" if request.scope["htmx"].hx_request else "-full"}.html'
    return templates.TemplateResponse(request, template, context={'view': view})
