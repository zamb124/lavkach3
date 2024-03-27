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
from app.bff.bff_service import BffService
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

@index_router.get("/bff/select", response_class=HTMLResponse)
@htmx(*s('widgets/select/select-htmx'))
async def select(
        request: Request,
        module: str,
        model: str,
        key: str = None,
        value: str = None,
        prefix: str = None,
        name: str = None,
        required=False

     ):
    """
     Универсальный запрос, который отдает список любого обьекта по его модулю и модели
    """
    field = request.query_params.get('field') or 'search'
    v = request.query_params.get('search_terms')
    params = QueryParams({field: v if v else ''})
    async with getattr(request.scope['env'], module) as a:
        data = await a.list(params=params, model=model)
    return {
        'name': name or model,
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
     Универсальный запрос, который отдает таблицу обьекта и связанные если нужно
    """
    from collections import defaultdict
    missing_fields = defaultdict(list)
    schema = config.services[module]['schema'][model]['base']
    async with getattr(request.scope['env'], module) as a:
        data = await a.list(params=request.query_params, model=model)
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
@htmx(*s('widgets/modal-crud/modal-edit-htmx'))
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
        data = await a.update(id=form_id, json=checked_form.model_dump(mode='json'), model=form_model)
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
    async with getattr(request.scope['env'], module) as a:
        data = await a.get(id=id, model=model)
    return {
        'module': module,
        'model': model,
        'data': data
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
async def modal_create_get(request: Request, module: str, model: str, id: str=None):
    """
     Универсальный запрос, который отдает модалку на подтвержлении удаления
    """
    """
         Универсальный запрос, который отдает форму модели (черпает из ModelUpdateSchema
        """

    schema = config.services[module]['schema'][model]['create']
    columns, _ = get_columns(module, model, schema)
    if id:
        columns.update({'id': {'val': id}}) # Если переходы идут от других модалок
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
    import json
    columns = {}
    form_data = await request.form()
    data = jsonable_encoder(form_data)
    schema = config.services[form_module]['schema'][form_model]['create']
    checked_form = schema(**data)
    async with getattr(request.scope['env'], form_module) as a:
        data = await a.create(json=checked_form.model_dump(mode='json'), model=form_model)
    return {
        'columns': columns,
        'module': form_module,
        'model': form_model,
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
