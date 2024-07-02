from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import HTMLResponse

from core.fastapi.frontend.schema_recognizer import ClassView
from app.bff.template_spec import templates

order_router = APIRouter()

class OrderView(ClassView):
    """Переопределяем модель"""
    model_name = "order"


    def get_store_dashboard(self):
        a=1

@order_router.get("", response_class=HTMLResponse)
async def order(request: Request):
    """
        Для построения фронта нам нужно передать в шаблон
        1 - схему
        2 - модуль/сервис и модель lля фильтрации
        3 - какие фильтры используем на странице (важно, что порядок будет тот же)
    """
    template = f'widgets/list{"" if request.scope["htmx"].hx_request else "-full"}.html'
    cls = await OrderView(request)
    return templates.TemplateResponse(request, template, context={'cls': cls})


@order_router.get("/mystore", response_class=HTMLResponse)
async def mystore(request: Request):
    """
        Отдает интерфейс склада с текущими ордерами и их статусами, так же текущими сотрудниками склада
    """
    template = f'widgets/list{"" if request.scope["htmx"].hx_request else "-full"}.html'
    order_cls = await OrderView(request)
    store_dash = order_cls.get_store_dashboard()
    return templates.TemplateResponse(request, template, context={'cls': cls})