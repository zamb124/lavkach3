from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import HTMLResponse

from core.fastapi.frontend.schema_recognizer import ClassView
from app.bff.template_spec import templates

move_router = APIRouter()


@move_router.get("", response_class=HTMLResponse)
async def move(request: Request):
    """
        Для построения фронта нам нужно передать в шаблон
        1 - схему
        2 - модуль/сервис и модель lля фильтрации
        3 - какие фильтры используем на странице (важно, что порядок будет тот же)
    """
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
