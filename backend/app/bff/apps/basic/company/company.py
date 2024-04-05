from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi_htmx import htmx

from app.bff.bff_server import config
from app.bff.dff_helpers.htmx_decorator import s
from app.bff.dff_helpers.schema_recognizer import ModelView

company_router = APIRouter()
@company_router.get("", response_class=HTMLResponse)
@htmx(*s('widgets/list'))
async def company(request: Request):
    model = ModelView(request, 'basic', 'company')
    return {'model': model}
