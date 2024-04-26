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
    cls = ClassView(request, 'move')
    return templates.TemplateResponse(request,'widgets/list-full.html', context={'cls': cls})
