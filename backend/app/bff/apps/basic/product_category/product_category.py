from typing import Annotated

from fastapi import APIRouter, Form
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi_htmx import htmx

from app.bff.dff_helpers.htmx_decorator import s

product_category_router = APIRouter()

@product_category_router.get("", response_class=HTMLResponse)
@htmx(*s('basic/product_category/product_category'))
async def product_category(request: Request):
    return {}


@product_category_router.get("/table", response_class=HTMLResponse)
@htmx(*s('basic/product_category/product_category-table'))
async def product_category_list(request: Request,):
    async with request.scope['env'].basic as oa:
        product_categorys_data = await oa.list(model='product_category', params=request.query_params) # Достаю склады
    return product_categorys_data


@product_category_router.post("", response_class=HTMLResponse)
@htmx(*s('helpers/informer'))
async def product_category_create(request: Request, company_id: Annotated[str, Form()], title: Annotated[str, Form()], address: Annotated[str, Form()]):
    async with request.scope['env'].basic as ba:
        _json = {
            'company_id': company_id,
            'title': title,
            'address': address
        }
        product_categorys_data = await ba.create(model='product_category', json=_json, params=request.query_params)  # Достаю склады
    return {'title': 'Company Created', 'Message': ''}
