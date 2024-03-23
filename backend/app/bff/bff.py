import asyncio
import datetime
import uuid
from typing import Annotated

import aiohttp
from fastapi import APIRouter
from fastapi import Form
from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse
from fastapi_htmx import htmx_init, htmx
from pydantic import BaseModel
from starlette.datastructures import QueryParams
from starlette.responses import Response

from app.bff.bff_config import config
from app.bff.dff_helpers.htmx_decorator import s
from app.bff.dff_helpers.schema_recognizer import get_columns
from app.bff.template_spec import templates

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
@htmx(*s('components/write_ls'))
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
    return {'token': data['token'], 'refresh_token': data['refresh_token']}

class RefreshTokenSchema(BaseModel):
    token: str
    refresh_token: str
@index_router.post("/auth/refresh_token", responses={"404": {"model": ExceptionResponseSchema}},)
async def refresh_token(request: Request, refresh_schema: RefreshTokenSchema):
    async with request.scope['env'].basic as a:
        return await a.refresh_token(refresh_schema)

@index_router.get("/bff/select", response_class=HTMLResponse)
@htmx(*s('widgets/select/select-htmx'))
async def select(request: Request, module: str, model: str, key: str = None, value: str = None, prefix: str = None, required=False):
    """
     Универсальный запрос, который отдает список любого обьекта по его модулю и модели
    """
    field = request.query_params.get('field') or 'search'
    v = request.query_params.get('search_terms')
    params = QueryParams({field: v if v else ''})
    async with getattr(request.scope['env'], module) as a:
        data = await a.list(params=params, model=model)
    return {
        'name': f'{module}_{model}_{field}',
        'module': module,
        'model': model,
        'prefix': prefix,
        'required': bool(required),
        'key': key,
        'value': value,
        'field': field,
        'objects': data if type(data) is list else data.get('data')
    }





@index_router.get("/base/table", response_class=HTMLResponse)
@htmx(*s('widgets/table/table-htmx'))
async def table(request: Request, module: str, model: str):
    """
     Универсальный запрос, который отдает таблицу обьекта
    """
    schema = config.services[module]['schema'][model]['base']
    async with getattr(request.scope['env'], module) as a:
        data = await a.list(params=request.query_params, model=model)
    columns, new_list = get_columns(module, model, schema, data['data'])
    return {
        'columns': [v.title if v.title else k for k, v in schema.model_fields.items()],
        'module': module,
        'cursor': data['cursor'],
        'model': model,
        'objects': new_list,
    }


@index_router.get("/base/modal-get", response_class=HTMLResponse)
@htmx(*s('widgets/modal-crud/modal-edit-htmx'))
async def modal_update_get(request: Request, module: str, model: str, id: uuid.UUID):
    """
     Универсальный запрос, который отдает форму модели (черпает из ModelUpdateSchema
    """
    schema = config.services[module]['schema'][model]['update']
    columns, _ = get_columns(module, model, schema)

    async with getattr(request.scope['env'], module) as a:
        data = await a.get(id=id, model=model)
    for k, v in columns.items():
        v['val'] = data[k]
    return {
        'columns': columns,
        'module': module,
        'model': model,
        'data': data
    }


@index_router.post("/base/modal-post", response_class=HTMLResponse)
@htmx(*s('components/message'))
async def modal_update_post(request: Request, form_module: str = Form(), form_model: str = Form(),
                            form_id: str = Form()):
    """
     Принимает форму на обновление модели
    """
    columns = {}
    form_data = await request.form()
    data = jsonable_encoder(form_data)
    schema = config.services[form_module]['schema'][form_model]['update']
    checked_form = schema(**data)
    async with getattr(request.scope['env'], form_module) as a:
        data = await a.update(id=form_id, json=checked_form.model_dump(), model=form_model)
    return {
        'columns': columns,
        'module': form_module,
        'model': form_model,
        'data': data,
        'message': f'{form_model.capitalize()} is updated'
    }


@index_router.get("/base/modal-delete", response_class=HTMLResponse)
@htmx(*s('widgets/modal-crud/modal-delete-htmx'))
async def modal_delete_get(request: Request, module: str, model: str, id: uuid.UUID):
    """
     Универсальный запрос, который отдает модалку на подтвержлении удаления
    """
    return {
        'module': module,
        'model': model,
        'id': id
    }


@index_router.delete("/base/modal-delete", response_class=HTMLResponse)
@htmx(*s('components/message'))
async def modal_delete_delete(request: Request, module: str, model: str, id: uuid.UUID):
    """
     Универсальный запрос, который отдает модалку на подтвержлении удаления
    """
    async with getattr(request.scope['env'], module) as a:
        await a.delete(id=id, model=model)
    return {
        'module': module,
        'model': model,
        'background': 'linear-gradient(to right, #00b09b, #96c93d)',
    }


@index_router.get("/base/modal-create", response_class=HTMLResponse)
@htmx(*s('widgets/modal-crud/modal-create-htmx'))
async def modal_create_get(request: Request, module: str, model: str):
    """
     Универсальный запрос, который отдает модалку на подтвержлении удаления
    """
    """
         Универсальный запрос, который отдает форму модели (черпает из ModelUpdateSchema
        """

    schema = config.services[module]['schema'][model]['create']
    columns, _ = get_columns(module, model, schema)
    return {
        'columns': columns,
        'module': module,
        'model': model,
    }


@index_router.post("/base/modal-create", response_class=HTMLResponse)
@htmx(*s('components/message'))
async def modal_create_post(request: Request, form_module: str = Form(), form_model: str = Form()):
    """
     Принимает форму создание
    """
    columns = {}
    form_data = await request.form()
    data = jsonable_encoder(form_data)
    schema = config.services[form_module]['schema'][form_model]['create']
    checked_form = schema(**data)
    async with getattr(request.scope['env'], form_module) as a:
        data = await a.create(json=checked_form.model_dump(), model=form_model)
    return {
        'columns': columns,
        'module': form_module,
        'model': form_model,
        'data': data,
        'message': f'{data.get("title")} is Created'
    }


@index_router.get("/base/card", response_class=HTMLResponse)
@htmx(*s('widgets/card/card-htmx'))
async def card(request: Request, module: str, model: str, id: str) -> dict:
    """
     Отдать карточку (title, created_at, updated_at)
    """
    async with getattr(request.scope['env'], module) as a:
        data = await a.get(id=id, model=model)
    return {
        'title': data['title'],
        'created_at': datetime.datetime.fromisoformat(data['created_at']),
        'updated_at': datetime.datetime.fromisoformat(data['created_at']),
    }
