from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse

from app.front.apps.inventory.views import SuggestView, ProductStorageTypeView
from app.front.template_spec import templates
from app.front.utills import render

product_storage_type_router = APIRouter()


@product_storage_type_router.get("", response_class=HTMLResponse)
async def product_storage_type(cls: ProductStorageTypeView = Depends()):
    """Список перемещений"""
    return await render(
        cls.r,
        f'widgets/list.html',
        context={'cls': cls}
    )


@product_storage_type_router.get("/line", response_class=HTMLResponse)
async def product_storage_type_line(suggest_id: UUID, suggest_view: SuggestView = Depends()):
    """Отдает лайну для монитора склада"""
    suggest = await suggest_view.get_lines(ids=[suggest_id])
    return await render(suggest_view.r, 'inventory/suggest/suggest_line.html', context={'suggest': suggest})
