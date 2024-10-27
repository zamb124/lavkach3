import uuid
from collections import defaultdict
from lib2to3.fixes.fix_input import context
from typing import Optional

from fastapi import APIRouter, Query
from fastapi import Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from starlette.responses import RedirectResponse
from starlette.websockets import WebSocket
from urllib3 import request

from app.front.apps.basic.company.company import company
from app.front.template_spec import templates
from app.front.utills import BasePermit
from distributed_websocket import WebSocketProxy

from app.front.front_config import config


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
