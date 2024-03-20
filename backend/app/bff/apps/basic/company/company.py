from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi_htmx import htmx

from app.bff.dff_helpers.htmx_decorator import s

company_router = APIRouter()


@company_router.get("", response_class=HTMLResponse)
@htmx(*s('basic/company/company'))
async def company(request: Request):
    return {}


@company_router.get("/table", response_class=HTMLResponse)
@htmx(*s('basic/company/company-table'))
async def company_list(request: Request):
    # async with CompanyAdapter(request) as ca:
    #     data = await ca.get_company_list()
    # return {
    #     'companies': data['data']
    # }
    ...

