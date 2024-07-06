from collections import defaultdict

from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from starlette.responses import RedirectResponse

from app.bff.template_spec import templates
from app.bff.utills import BasePermit


class ExceptionResponseSchema(BaseModel):
    error: str


index_router = APIRouter(
    responses={"400": {"model": ExceptionResponseSchema}},
)


@index_router.get("/", response_class=HTMLResponse)
async def root_page(request: Request):
    if not request.user.user_id:
        return RedirectResponse("/landing")
    return RedirectResponse("/inventory/dashboard")


@index_router.get("/landing", response_class=HTMLResponse)
async def root_page(request: Request):
    return templates.TemplateResponse(request, 'landing.html', context={})


@index_router.get("/bff/footer", response_class=HTMLResponse)
async def footer(request: Request):
    return templates.TemplateResponse(request, 'partials/footer.html', context={})


@index_router.get("/bff/topbar", response_class=HTMLResponse)
async def topbar(request: Request):
    return templates.TemplateResponse(request, 'partials/topbar.html', context={})


@index_router.get("/bff/sidebar", response_class=HTMLResponse)
async def sidebar(request: Request):
    """Строит левое меню Админки, на базе tags в роутах и пермишенах Пользователя"""
    domains = {}
    is_admin = request.user.is_admin
    async with request.scope['env']['company'].adapter as ad:
        permits = await ad.permissions(user_id=request.user.user_id)
    for route in filter(lambda r: hasattr(r, 'dependencies'), request.app.routes):
        for dependency in route.dependencies:
            if issubclass(dependency.dependency, BasePermit):
                if is_admin or any(elem in dependency.dependency.permits for elem in permits):
                    try:
                        domain_name, model_name = route.tags
                    except:
                        continue
                    if domain := domains.get(domain_name):
                        domain[model_name].append(route)
                    else:
                        domains[domain_name] = defaultdict(list)
                        domains[domain_name][model_name].append(route)

    return templates.TemplateResponse(
        request, 'partials/sidebar.html', context={'domains': domains}
    )


@index_router.get("/", response_class=HTMLResponse)
async def root_page(request: Request):
    return templates.TemplateResponse(request, 'index.html', context={'ws_domain': ws_domain})


@index_router.get("/basic/dropdown-ids", response_class=HTMLResponse)
async def dropdown_ids(request: Request, module: str, model: str, id: str, itemlink: str, is_named=False) -> dict:
    """
     Виджет на вход получает модуль-модель-ид- и обратную ссылку если нужно, если нет будет /module/model/{id}
     _named означает, что так же будет отдат name для отрисовки на тайтле кнопки
    """
    data = await request.scope['env']['company'].adapter.dropdown_ids(model, id, itemlink, is_named)
    return templates.TemplateResponse(request, 'widgets/dropdown-ids-named-htmx.html', context=data)
