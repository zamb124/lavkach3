import uuid
from typing import Annotated

from fastapi import APIRouter, Form
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi_htmx import htmx

from app.bff.dff_helpers.htmx_decorator import s

store_router = APIRouter()

@store_router.get("", response_class=HTMLResponse)
@htmx(*s('basic/store/store'))
async def store(request: Request):
    return {}


@store_router.get("/table", response_class=HTMLResponse)
@htmx(*s('basic/store/store-table'))
async def store_list(request: Request,):
    async with request.scope['env'].basic as oa:
        stores_data = await oa.list(model='store', params=request.query_params) # Достаю склады
    return stores_data
@store_router.post("", response_class=HTMLResponse)
@htmx(*s('helpers/informer'))
async def store_create(request: Request, company_id: Annotated[str, Form()], title: Annotated[str, Form()], address: Annotated[str, Form()]):
    async with request.scope['env'].basic as ba:
        _json = {
            'company_id': company_id,
            'title': title,
            'address': address
        }
        stores_data = await ba.create(model='store', json=_json, params=request.query_params)  # Достаю склады
    return {'title': 'Store Created', 'Message': ''}

@store_router.delete("/{store_id}", response_class=HTMLResponse)
@htmx(*s('helpers/informer'))
async def store_create(request: Request, store_id: uuid.UUID):
    async with request.scope['env'].basic as ba:
        stores_data = await ba.delete(model='store', id=store_id, params=request.query_params)  # Достаю склады
    return {'title': 'Store Deleted', 'Message': ''}

@store_router.get("/{store_id}", response_class=HTMLResponse)
@htmx(*s('basic/store/table/row/store-edit-row'))
async def store_edit_row(request: Request, store_id: uuid.UUID):
    async with request.scope['env'].basic as ba:
        store_data = await ba.get(model='store', id=store_id, params=request.query_params)  # Достаю склады
    return {'title': 'Store Deleted', 'Message': ''}
