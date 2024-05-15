from typing import Annotated

from fastapi import APIRouter
from fastapi import Form
from fastapi import Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from starlette.responses import Response

from app.bff.bff_config import config
from app.bff.template_spec import templates


class ExceptionResponseSchema(BaseModel):
    error: str


index_router = APIRouter(
    responses={"400": {"model": ExceptionResponseSchema}},
)


@index_router.get("/", response_class=HTMLResponse)
async def root_page(request: Request):
    return templates.TemplateResponse(request, 'index-full.html', context={})


@index_router.get("/bff/footer", response_class=HTMLResponse)
async def footer(request: Request):
    return templates.TemplateResponse(request, 'partials/footer.html', context={})


@index_router.get("/bff/topbar", response_class=HTMLResponse)
async def topbar(request: Request):
    return templates.TemplateResponse(request, 'partials/topbar.html', context={})


@index_router.get("/", response_class=HTMLResponse)
async def root_page(request: Request):
    return templates.TemplateResponse(request, 'index.html', context={'ws_domain': ws_domain})


@index_router.get("/basic/login", responses={"404": {"model": ExceptionResponseSchema}}, )
async def login(request: Request, response: Response):
    return templates.TemplateResponse(request, 'basic/login-full.html', context={})


@index_router.post(
    "/basic/login",
    responses={"404": {"model": ExceptionResponseSchema}},
)
async def login(
        request: Request,
        username: Annotated[str, Form()],
        password: Annotated[str, Form()]):
    request.scope['env']
    async with request.scope['env']['user'].adapter as a:
        data = await a.login(username, password)
    return templates.TemplateResponse(request, 'components/write_ls.html', context={'token': data['token'], 'refresh_token': data['refresh_token']})


class RefreshTokenSchema(BaseModel):
    token: str
    refresh_token: str


@index_router.post("/basic/user/refresh", responses={"404": {"model": ExceptionResponseSchema}}, )
async def refresh_token(request: Request, refresh_schema: RefreshTokenSchema):
    async with request.scope['env']['user'].adapter as a:
        return await a.refresh_token(refresh_schema)



@index_router.get("/basic/dropdown-ids", response_class=HTMLResponse)
async def dropdown_ids(request: Request, module: str, model: str, id: str, itemlink: str, is_named=False) -> dict:
    """
     Виджет на вход получает модуль-модель-ид- и обратную ссылку если нужно, если нет будет /module/model/{id}
     _named означает, что так же будет отдат name для отрисовки на тайтле кнопки
    """
    data = await request.scope['env']['company'].adapter.dropdown_ids(model, id, itemlink, is_named)
    return templates.TemplateResponse(request, 'widgets/dropdown-ids-named-htmx.html', context=data)
