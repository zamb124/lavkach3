from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import HTMLResponse

from core.fastapi.frontend.schema_recognizer import ClassView
from app.bff.template_spec import templates

order_router = APIRouter()

@order_router.get("", response_class=HTMLResponse)
async def order(request: Request):
    """
        Для построения фронта нам нужно передать в шаблон
        1 - схему
        2 - модуль/сервис и модель lля фильтрации
        3 - какие фильтры используем на странице (важно, что порядок будет тот же)
    """
    template = f'widgets/list{"" if request.scope["htmx"].hx_request else "-full"}.html'
    cls = ClassView(request, model='order')
    return templates.TemplateResponse(request, template, context={'cls': cls})
