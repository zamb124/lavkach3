import asyncio
from typing import Annotated
from fastapi import Form
import aiohttp
from fastapi import APIRouter
from fastapi import Request
from starlette.datastructures import QueryParams
from starlette.responses import Response
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from fastapi_htmx import htmx_init, htmx

from core.fastapi.adapters.base_adapter import BaseAdapter
from app.bff.template_spec import templates
from app.bff.dff_helpers.htmx_decorator import s

htmx_init(templates, file_extension='html')


class ExceptionResponseSchema(BaseModel):
    error: str


index_router = APIRouter(
    responses={"400": {"model": ExceptionResponseSchema}},
)


@index_router.get("/", response_class=HTMLResponse)
@htmx(*s('index'))
async def root_page(request: Request):
    return {"greeting": "Hello World"}


@index_router.get("/htmx/footer", response_class=HTMLResponse)
@htmx(*s('partials/footer'))
async def footer(request: Request):
    await asyncio.sleep(5)
    return {"greeting": "Hello World"}


@index_router.get("/htmx/topbar", response_class=HTMLResponse)
@htmx(*s('partials/topbar'))
async def topbar(request: Request):
    return {"greeting": "Hello World"}


@index_router.get("/", response_class=HTMLResponse)
@htmx(*s('index'))
async def root_page(request: Request):
    return {"greeting": "Hello World"}


@index_router.get(
    "/auth/login",
    responses={"404": {"model": ExceptionResponseSchema}},
)
@htmx(*s('auth/login'))
async def login(request: Request, response: Response):
    return {}


@index_router.post(
    "/auth/login",
    responses={"404": {"model": ExceptionResponseSchema}},
)
@htmx(*s('helpers/write_ls'))
async def login(
        request: Request,
        response: Response,
        username: Annotated[str, Form()],
        password: Annotated[str, Form()]):
    async with aiohttp.ClientSession() as session:
        body = {
            'email': username,
            'password': password
        }
        async with session.post('http://127.0.0.1:8001/api/basic/user/login', json=body) as bresp:
            data = await bresp.json()
    response.set_cookie(key='token', value=data['token'], httponly=True)
    response.set_cookie(key='refresh_token', value=data['refresh_token'], httponly=True)
    return {'token': data['token'], 'refresh_token': data['refresh_token']}


@index_router.get("/bff/select", response_class=HTMLResponse)
@htmx(*s('helpers/choices'))
async def select(request: Request):
    trigger_component = request.query_params.get('target_component') or 'table'
    module = request.query_params.get('module')
    model = request.query_params.get('model')
    field = request.query_params.get('field') or 'search'
    return_field_name = request.query_params.get('return_field_name')
    v = request.query_params.get('search_terms')
    params = QueryParams({field: v if v else ''})
    async with getattr(request.scope['env'], module) as a:
        data = await a.list(params=params, model=model)
    return {
        'name': f'{module}_{model}_{field}',
        'module': module,
        'model': model,
        'field': field,
        'trigger_component': f"#{trigger_component}",
        'return_field_name': return_field_name,
        'objects': data['data']
    }

