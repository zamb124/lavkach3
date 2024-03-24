from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi_htmx import htmx

from app.bff.bff_server import config
from app.bff.dff_helpers.htmx_decorator import s
from app.bff.dff_helpers.schema_recognizer import get_columns

order_router = APIRouter()
@order_router.get("", response_class=HTMLResponse)
@htmx(*s('inventory/order/order'))
async def order(request: Request):
    """
        Для построения фронта нам нужно передать в шаблон
        1 - схему
        2 - модуль/сервис и модель lля фильтрации
        3 - какие фильтры используем на странице (важно, что порядок будет тот же)
    """
    schema = config.services['inventory']['schema']['order']['filter']
    columns, _ = get_columns('inventory', 'order', schema, exclude=['updated_at__gte', 'updated_at__lt', 'updated_at'])
    return {
        'module': 'inventory',
        'model': 'order',
        'columns': columns,
    }
