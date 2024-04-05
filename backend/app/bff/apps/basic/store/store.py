from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi_htmx import htmx

from app.bff.dff_helpers.htmx_decorator import s
from app.bff.dff_helpers.schema_recognizer import ModelView

store_router = APIRouter()


@store_router.get("", response_class=HTMLResponse)
@htmx(*s('widgets/list'))
async def store(request: Request):
    model = ModelView(request, 'basic', 'store')
    return {'model': model}
