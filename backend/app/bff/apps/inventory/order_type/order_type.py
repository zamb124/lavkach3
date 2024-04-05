from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi_htmx import htmx

from app.bff.dff_helpers.htmx_decorator import s
from app.bff.dff_helpers.schema_recognizer import ModelView

order_type_router = APIRouter()


@order_type_router.get("", response_class=HTMLResponse)
@htmx(*s('widgets/list'))
async def order_type(request: Request):
    """
        Для построения фронта нам нужно передать в шаблон
        1 - схему
        2 - модуль/сервис и модель lля фильтрации
        3 - какие фильтры используем на странице (важно, что порядок будет тот же)
    """
    model = ModelView(request, 'inventory', 'order_type')

    return {'model': model}
