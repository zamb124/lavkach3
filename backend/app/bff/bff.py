import asyncio
import datetime
import typing
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


def get_module_by_model(model):
    for k, v in config.services.items():
        if v['schema'].get(model):
            return k


def dict_obj_format(k, val: str, module: dict):
    return {
        'type': 'dict_obj',
        'module': module,
        'val': val
    }


def date_format(k, val: str, module=None):
    return {
        'type': 'datetime',
        'module': module,
        'val': datetime.datetime.fromisoformat(val)
    }


def uuid_format(k, v: uuid.UUID, module=None):
    return {
        'type': 'uuid',
        'module': module,
        'val': v
    }


def str_format(k, v: str, module=None):
    return {
        'type': 'str',
        'module': module,
        'val': v
    }


def str_link_format(k, v: str, module=None):
    """
    Если переменная заканчивает на _id, то понимаем, что это id какой то модели,
    Ищем в каком она сервисе с помощью get_module_by_model перебирая конфиг
    """
    return {
        'type': 'str_link',
        'module': module,
        'val': v,
        'link_module': get_module_by_model(k[0:-3]),  # подразумевается, что откусываем '_id'
        'link_model': k[0:-3]
    }


def recognize_type(module: str, model: str, k: str, fielinfo):
    """
    Для шаблонизатора распознаем тип для удобства HTMX (универсальные компоненты)
    """
    res = 'str'
    if fielinfo.annotation == typing.Optional[str]:
        res = 'str'
    elif k == 'country':
        res = 'country'
        model = 'country'
    elif k == 'phone':
        res = 'phone'
    elif k == 'currency':
        res = 'currency'
        model = 'currency'
    elif k == 'locale':
        res = 'locale'
        model = 'locale'
    elif k.endswith('_id') and k not in ('external_number',):
        res = 'model'
        module = get_module_by_model(model[0:-3])
    elif k.endswith('_ids'):
        res = 'list'
    elif fielinfo.annotation == typing.Optional[datetime.datetime] or fielinfo.annotation == datetime.datetime:
        res = 'datetime'
    return {
        'type': res,
        'module': module,
        'model': model,
        'required': fielinfo.is_required()
    }


def get_columns(module, model, schema, data=None):
    columns = {}
    for k, v in schema.model_fields.items():
        columns.update({
            k: recognize_type(module, model, k, v)
        })
    if data:
        for row in data:
            for col, val in row.items():
                row[col] = {
                    **columns[col],
                    'val': datetime.datetime.fromisoformat(val) if columns[col]['type'] == 'datetime' else val
                }
    return columns, data


@index_router.get("/base/table", response_class=HTMLResponse)
@htmx(*s('base/table'))
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
@htmx(*s('base/modal-edit'))
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
@htmx(*s('base/toast'))
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
@htmx(*s('base/modal-delete'))
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
@htmx(*s('base/toast'))
async def modal_delete_delete(request: Request, module: str, model: str, id: uuid.UUID):
    """
     Универсальный запрос, который отдает модалку на подтвержлении удаления
    """
    async with getattr(request.scope['env'], module) as a:
        data = await a.delete(id=id, model=model)
    return {
        'module': module,
        'model': model,
        'background': 'linear-gradient(to right, #00b09b, #96c93d)',
    }


@index_router.get("/base/modal-create", response_class=HTMLResponse)
@htmx(*s('base/modal-create'))
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
@htmx(*s('base/toast'))
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
@htmx(*s('base/card'))
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
