from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi_htmx import htmx

from app.bff.dff_helpers.htmx_decorator import s

company_router = APIRouter()


@company_router.get("", response_class=HTMLResponse)
@htmx(*s('basic/company/company'))
async def company(request: Request):
    return {
        'module': 'basic',
        'model': 'company'
    }
