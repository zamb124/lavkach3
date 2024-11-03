import asyncio
import json
import os
import uuid
from collections import defaultdict
from lib2to3.fixes.fix_input import context
from typing import Optional
import re

import aiofiles
from fastapi import APIRouter, Query
from fastapi import Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from starlette.responses import RedirectResponse, JSONResponse
from starlette.websockets import WebSocket
from urllib3 import request

from app.front.apps.basic.company.company import company
from app.front.template_spec import templates
from app.front.utills import BasePermit
from distributed_websocket import WebSocketProxy

from app.front.front_config import config
from core.frontend.constructor import BaseSchema
from core.frontend.enviroment import template_dirs


class ExceptionResponseSchema(BaseModel):
    error: str


index_router = APIRouter(
    responses={"400": {"model": ExceptionResponseSchema}},
)


@index_router.get("/front/topbar_vertical", response_class=HTMLResponse)
async def topbar(request: Request):
    return templates.TemplateResponse(request, 'partials/topbar_vertical.html', context={})


@index_router.get("/front/topbar_horizontal", response_class=HTMLResponse)
async def topbar(request: Request):
    return templates.TemplateResponse(request, 'partials/topbar_horizontal.html', context={})


@index_router.get("/front/theme_editor", response_class=HTMLResponse)
async def topbar(request: Request):
    return templates.TemplateResponse(request, 'partials/theme_editor.html', context={})


@index_router.get("/front/search_bar", response_class=HTMLResponse)
async def topbar(request: Request):
    return templates.TemplateResponse(request, 'partials/search_bar.html', context={})


@index_router.get("/front/sidebar_vertical", response_class=HTMLResponse)
async def sidebar(request: Request):
    """Строит левое меню Админки, на базе tags в роутах и пермишенах Пользователя"""
    admin_nav = {}
    env = request.scope['env']
    for domain_name, domain in env.domains.items():
        model_list = {}
        for model_name, model in domain.models.items():
            model_list.update({
                model_name: f'/{domain_name}/{model_name}',
            })
        admin_nav.update({
            domain_name: model_list
        })
    return templates.TemplateResponse(request, 'partials/sidebar_vertical.html',
                                      context={'nav': admin_nav})


@index_router.get("/front/sidebar_horizontal", response_class=HTMLResponse)
async def sidebar(request: Request):
    """Строит левое меню Админки, на базе tags в роутах и пермишенах Пользователя"""
    return templates.TemplateResponse(request, 'partials/sidebar_horizontal.html')


@index_router.get("/front/sidebar", response_class=HTMLResponse)
async def sidebar(request: Request):
    """Строит левое меню Админки, на базе tags в роутах и пермишенах Пользователя"""
    return templates.TemplateResponse(request, 'partials/sidebar.html')


@index_router.get("/front/sidebar_scroll", response_class=HTMLResponse)
async def sidebar(request: Request):
    """Строит левое меню Админки, на базе tags в роутах и пермишенах Пользователя"""
    return templates.TemplateResponse(request, 'partials/sidebar_scroll.html')


@index_router.get("/front/search_bar", response_class=HTMLResponse)
async def sidebar(request: Request):
    """Строит левое меню Админки, на базе tags в роутах и пермишенах Пользователя"""
    return templates.TemplateResponse(request, 'partials/search_bar.html')


@index_router.get("/front/theme_editor", response_class=HTMLResponse)
async def sidebar(request: Request):
    """Строит левое меню Админки, на базе tags в роутах и пермишенах Пользователя"""
    return templates.TemplateResponse(request, 'partials/theme_editor.html')


@index_router.get("/", response_class=HTMLResponse)
async def root_page(request: Request):
    return templates.TemplateResponse(request, 'index-full.html')


async def get_user_companies(request: Request) -> dict:
    async with request.scope['env']['company'].adapter as a:
        res = await a.list(params={'id__in': request.user.company_ids})
        companies = {i['id']: i for i in res['data']}
        company = companies.get(request.user.company_id.__str__())
        companies.pop(request.user.company_id.__str__())
    return {
        'companies': companies,
        'company': company
    }


@index_router.get("/front/company_changer_widget", response_class=HTMLResponse)
async def company_changer_widget(request: Request) -> dict:
    data = await get_user_companies(request)
    return templates.TemplateResponse(request, 'widgets/widget_company_changer.html', context=data)


class CompanyId(BaseModel):
    company_id: uuid.UUID


@index_router.post("/front/company_changer_widget", response_class=HTMLResponse)
async def company_changer_widget(request: Request, schema: CompanyId) -> dict:
    async with request.scope['env']['user'].adapter as a:
        data = await a.user_company_change(user_id=request.user.user_id,
                                           company_id=schema.company_id)
    data = await get_user_companies(request)
    return templates.TemplateResponse(request, 'widgets/widget_company_changer.html', context=data)


# @index_router.get("/basic/dropdown-ids", response_class=HTMLResponse)
# async def dropdown_ids(request: Request, module: str, model: str, id: str, itemlink: str,
#                        is_named=False) -> dict:
#     """
#      Виджет на вход получает модуль-модель-ид- и обратную ссылку если нужно, если нет будет /module/model/{id}
#      _named означает, что так же будет отдат name для отрисовки на тайтле кнопки
#     """
#     data = await request.scope['env']['company'].adapter.dropdown_ids(model, id, itemlink, is_named)
#     return templates.TemplateResponse(request, 'widgets/dropdown-ids-named-htmx.html', context=data)

@index_router.get("/front/widget_locale_changer", response_class=HTMLResponse)
async def company_changer_widget(request: Request, locale: str=None) -> dict:
    locales = {
        'current_locale': locale or request.cookies.get('locale') or request.user.locale,
        'locales': [
            'en',
            'ru',
            'sa'
        ]
    }
    if locale and locale != request.user.locale:
        async with request.scope['env']['user'].adapter as a:
            await a.user_locale_change(user_id=request.user.user_id, locale=locale)
    return templates.TemplateResponse(
        request,
        'widgets/widget_locale_changer.html',
        context=locales
    )


@index_router.get("/front/widget_user_profile", response_class=HTMLResponse)
async def widget_user_profile(request: Request) -> dict:
    return templates.TemplateResponse(
        request,
        'widgets/widget_user_profile.html'
    )




async def find_data_keys_in_file(file_path):
    data_keys = set()
    pattern = re.compile(r'data-key="([^"]+)"')

    async with aiofiles.open(file_path, mode='r', encoding='utf-8') as file:
        try:
            content = await file.read()
        except Exception as ex:
            return set()
        matches = pattern.findall(content)
        data_keys.update(matches)

    return data_keys


async def find_data_keys(directories):
    data_keys = set()

    async def process_directory(directory):
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(".html"):
                    file_path = os.path.join(root, file)
                    file_data_keys = await find_data_keys_in_file(file_path)
                    data_keys.update(file_data_keys)

    tasks = [process_directory(directory) for directory in directories]
    await asyncio.gather(*tasks)

    return [i for i in data_keys if '{' not in i]


@index_router.get("/front/translate_keys", response_class=JSONResponse)
async def geterate_translate_keys(request: Request, locale: str) -> dict:
    env = request.scope['env']
    path = f'app/front/static/i18n/{locale}.json'
    async with aiofiles.open(path, mode='r') as file:
        content = await file.read()
        keys = json.loads(content)
    init_keys = {}
    for domain_name, domain in env.domains.items():
        for model_name, model in domain.models.items():
            schema_keys = []
            for shema_name, schema in model.schemas.__dict__.items():
                try:
                    if issubclass(schema, BaseModel):
                        fields = (schema.model_fields | schema.model_computed_fields).keys()
                        schema_keys += fields
                except Exception as ex:
                    continue
            cleaned_schema_keys = list(set(schema_keys))
            for key in cleaned_schema_keys:
                init_keys.update({f't-{model_name}-{key}': None})
    init_keys.update(keys)
    data = await find_data_keys(template_dirs)
    for data_key in data:
        if to_add_key := not init_keys.get(data_key):
            init_keys.update({data_key: None})
    return init_keys
