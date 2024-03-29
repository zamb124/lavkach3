import asyncio
import datetime
import uuid
from collections import defaultdict
from typing import Annotated, Optional, Any

import aiohttp
from fastapi import APIRouter
from fastapi import Form
from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse
from fastapi_htmx import htmx_init, htmx
from pydantic import BaseModel, field_validator, UUID4
from starlette.datastructures import QueryParams
from starlette.responses import Response

from app.bff.bff_config import config
from app.bff.bff_service import BffService
from app.bff.dff_helpers.filters_cleaner import clean_filter
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
@index_router.post("/basic/user/refresh", responses={"404": {"model": ExceptionResponseSchema}},)
async def refresh_token(request: Request, refresh_schema: RefreshTokenSchema):
    async with request.scope['env'].basic as a:
        return await a.refresh_token(refresh_schema)

class SelectSchema(BaseModel):
    module: str
    model: str
    prefix: str
    name: str
    value: str = None
    required: bool = False
    title: str = None
    search_terms: Any = None

    @field_validator('value')
    @classmethod
    def check_none(cls, v: Any):
        if v == 'None':
            return None
        return v

    @field_validator('required', 'value')
    @classmethod
    def check_none(cls, v: Any):
        if v == 'None':
            return None
        return v

@index_router.post("/bff/select", response_class=HTMLResponse)
@htmx(*s('widgets/select/select-htmx'))
async def select(request: Request, selschema: SelectSchema):
    """
     Универсальный запрос, который отдает список любого обьекта по его модулю и модели
    """
    v = selschema.search_terms
    params = QueryParams({'search': v if v else ''})
    async with getattr(request.scope['env'], selschema.module) as a:
        data = await a.list(params=params, model=selschema.model)
    if selschema.value:
        for i in data['data']:
            if selschema.value == i['id']:
                selschema.title = i.get('title') or i.get('code') or i.get('english_language') or i.get('nickname')
    return {
        'name': selschema.name,
        'module': selschema.module,
        'model': selschema.model,
        'prefix': selschema.prefix,
        'required': selschema.required,
        'value': selschema.value,
        'title': selschema.title,
        'objects': data if type(data) is list else data.get('data')
    }






@index_router.get("/base/table", response_class=HTMLResponse)
@htmx(*s('widgets/table/table-htmx'))
async def table(request: Request, module: str, model: str, filter='filter:'):
    """
     Универсальный запрос, который отдает таблицу обьекта и связанные если нужно
    """

    missing_fields = defaultdict(list)
    schema = config.services[module]['schema'][model]['base']
    async with getattr(request.scope['env'], module) as a:
        qp = clean_filter(request.query_params, filter)
        data = await a.list(params=qp, model=model)
    columns, table = get_columns(module, model, schema, data['data'])
    for line in table:
        """Достаем все релейтед обьекты"""
        for field, value in line.items():
            if value.get('is_miss_table'):
                if value['val']:
                    missing_fields[f'{field}.{value["module"]}.{value["model"]}'].append(value['val'])
    for miss_key, miss_value in missing_fields.items():
        _field, _module, _model = miss_key.split('.')
        async with getattr(request.scope['env'], _module) as a:
            qp = QueryParams({'id__in': miss_value})
            _data = await a.list(params=qp, model=_model)
        _join_lines = {i['id']: i for i in _data['data']}
        if _field.endswith('_by'):
            new_field = _field.replace('_by', '_rel')
        else:
            new_field = _field.replace('_id', '_rel')
        columns.update({new_field: {'widget': {'table': True}}})
        for line in table:
            line.update({
                new_field: {
                    'model': _model,
                    'module': _module,
                    'required': False,
                    'enums': [],
                    'title': columns[_field]['title'],
                    'type': 'model_rel',
                    'widget': {'table': True},
                    'val': _join_lines[line[_field]['val']]
                }
            })
            line.pop(_field)
        columns.pop(_field)

    return {
        'columns': columns,
        'module': module,
        'cursor': data['cursor'],
        'model': model,
        'objects': table,
    }


@index_router.get("/base/modal-get", response_class=HTMLResponse)
@htmx(*s('widgets/modal-crud/modal-update-htmx'))
async def modal_update_get(request: Request, module: str, model: str, id: uuid.UUID):
    """
     Универсальный запрос, который отдает форму модели (черпает из ModelUpdateSchema
    """
    schema = config.services[module]['schema'][model]['update']


    async with getattr(request.scope['env'], module) as a:
        data = await a.get(id=id, model=model)
    columns, data = get_columns(module, model, schema, data=[data,])
    return {
        'columns': data[0],
        'module': module,
        'model': model,
        'id': id
    }

class FormUpdateSchema(BaseModel):
    modal_update_module: str
    modal_update_model: str
    modal_update_id: UUID4

    class Config:
        extra = 'allow'

@index_router.post("/base/modal-post", response_class=HTMLResponse)
@htmx(*s('components/message'))
async def modal_update_post(request: Request, schema: FormUpdateSchema):
    """
     Принимает форму на обновление модели
    """
    columns = {}
    form_data = await request.json()
    data = clean_filter(form_data, 'modal_update:')
    module_schema = config.services[schema.modal_update_module]['schema'][schema.modal_update_model]['update']
    checked_form = module_schema(**data)
    async with getattr(request.scope['env'], schema.modal_update_module) as a:
        data = await a.update(id=schema.modal_update_id, json=checked_form.model_dump(mode='json'), model=schema.modal_update_model)
    return {
        'columns': columns,
        'module': schema.modal_update_module,
        'model': schema.modal_update_model,
        'data': data,
        'message': f'{schema.modal_update_model.capitalize()} is updated'
    }


@index_router.get("/base/modal-delete", response_class=HTMLResponse)
@htmx(*s('widgets/modal-crud/modal-delete-htmx'))
async def modal_delete_get(request: Request, module: str, model: str, id: uuid.UUID):
    """
     Универсальный запрос, который отдает модалку на подтвержлении удаления
    """
    async with getattr(request.scope['env'], module) as a:
        data = await a.get(id=id, model=model)
    return {
        'module': module,
        'model': model,
        'data': data,
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
        'background': 'linear-gradient(to right, #e94e1d, #e94e1d)',
        'message': f'{model.capitalize()} is deleted'
    }


@index_router.get("/base/modal-create", response_class=HTMLResponse)
@htmx(*s('widgets/modal-crud/modal-create-htmx'))
async def modal_create_get(request: Request, module: str, model: str, id: str=None):
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
        'id': id
    }

class FormCreateSchema(BaseModel):
    modal_create_module: str
    modal_create_model: str

@index_router.post("/base/modal-create", response_class=HTMLResponse)
@htmx(*s('components/message'))
async def modal_create_post(request: Request, schema: FormCreateSchema):
    """
     Принимает форму создание
    """
    columns = {}
    form_data = await request.json()
    data = clean_filter(form_data, 'modal_create:')
    create_schema = config.services[schema.modal_create_module]['schema'][schema.modal_create_model]['create']
    checked_form = create_schema(**data)
    async with getattr(request.scope['env'], schema.modal_create_module) as a:
        data = await a.create(json=checked_form.model_dump(mode='json'), model=schema.modal_create_model)
    return {
        'columns': columns,
        'module': schema.modal_create_module,
        'model': schema.modal_create_model,
        'data': data,
        'message': f'{data.get("title")} is Created'
    }

@index_router.get("/base/modal-view", response_class=HTMLResponse)
@htmx(*s('widgets/modal-crud/modal-view-htmx'))
async def modal_view_get(request: Request, module: str, model: str, id: uuid.UUID):
    """
     Универсальный запрос, который отдает форму модели на просмотр
    """
    schema = config.services[module]['schema'][model]['base']

    async with getattr(request.scope['env'], module) as a:
        data = await a.get(id=id, model=model)
    columns, data = get_columns(module, model, schema, [data,])
    return {
        'columns': data[0],
        'module': module,
        'model': model,
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

@index_router.get("/base/dropdown-ids", response_class=HTMLResponse)
@htmx(*s('widgets/widgets/dropdown-ids-named-htmx'))
async def dropdown_ids(request: Request, module: str, model: str, id: str, itemlink: str, is_named=False) -> dict:
    """
     Виджет на вход получает модуль-модель-ид- и обратную ссылку если нужно, если нет будет /module/model/{id}
     _named означает, что так же будет отдат name для отрисовки на тайтле кнопки
    """
    return await BffService.dropdown_ids(request,module, model, id, itemlink, is_named)
