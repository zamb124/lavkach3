from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi_htmx import htmx, htmx_init
from starlette.templating import Jinja2Templates

from app.bff.dff_helpers.htmx_decorator import s

company_router = APIRouter()


@company_router.get("/list", response_class=HTMLResponse)
@htmx(*s('basic/company/company-table'))
async def root_page(request: Request):
    return {"greeting": "Hello World"}
