from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi_htmx import htmx

from app.bff.bff_server import config
from app.bff.dff_helpers.htmx_decorator import s
from app.bff.dff_helpers.schema_recognizer import get_columns

store_router = APIRouter()
@store_router.get("", response_class=HTMLResponse)
@htmx(*s('basic/store/store'))
async def store(request: Request):
    """
        Для построения фронта нам нужно передать в шаблон
        1 - схему
        2 - модуль/сервис и модель lля фильтрации
        3 - какие фильтры используем на странице (важно, что порядок будет тот же)
    """
    schema = config.services['basic']['schema']['store']['filter']
    columns, _ = get_columns('basic', 'store', schema)
    return {
        'module': 'basic',
        'model': 'store',
        'id': request.user.store_ids[0],
        'columns': columns,
    }
