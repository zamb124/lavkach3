from collections import defaultdict

from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from starlette.responses import RedirectResponse

from app.front.template_spec import templates
from app.front.utills import BasePermit


class ExceptionResponseSchema(BaseModel):
    error: str


index_router = APIRouter(
    responses={"400": {"model": ExceptionResponseSchema}},
)


@index_router.get("/front/header", response_class=HTMLResponse)
async def topbar(request: Request):
    return templates.TemplateResponse(request, 'partials/header.html', context={})


@index_router.get("/front/sidebar", response_class=HTMLResponse)
async def sidebar(request: Request):
    """Строит левое меню Админки, на базе tags в роутах и пермишенах Пользователя"""
    return templates.TemplateResponse(request, 'partials/sidebar.html')


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


@index_router.get("/basic/dropdown-ids", response_class=HTMLResponse)
async def dropdown_ids(request: Request, module: str, model: str, id: str, itemlink: str,
                       is_named=False) -> dict:
    """
     Виджет на вход получает модуль-модель-ид- и обратную ссылку если нужно, если нет будет /module/model/{id}
     _named означает, что так же будет отдат name для отрисовки на тайтле кнопки
    """
    data = await request.scope['env']['company'].adapter.dropdown_ids(model, id, itemlink, is_named)
    return templates.TemplateResponse(request, 'widgets/dropdown-ids-named-htmx.html', context=data)
