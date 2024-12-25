from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse

from app.front.apps.inventory.views import SuggestView, ProductStorageTypeView, StorageTypeView
from app.front.template_spec import templates
from app.front.utills import render

storage_type_router = APIRouter()


@storage_type_router.get("", response_class=HTMLResponse)
async def product_storage_type(cls: StorageTypeView = Depends()):
    """Список перемещений"""
    template = f'widgets/list{"" if cls.r.scope["htmx"].hx_request else "-full"}.html'
    return templates.TemplateResponse(cls.r, template, context={'cls': cls})


@storage_type_router.get("/line", response_class=HTMLResponse)
async def product_storage_type_line(suggest_id: UUID, suggest_view: SuggestView = Depends()):
    """Отдает лайну для монитора склада"""
    suggest = await suggest_view.get_lines(ids=[suggest_id])
    return await render(suggest_view.r, 'inventory/suggest/suggest_line.html', context={'suggest': suggest})
