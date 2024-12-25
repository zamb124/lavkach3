from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse

from app.front.apps.inventory.views import MoveLogView
from app.front.template_spec import templates
from app.front.utills import render

move_log_router = APIRouter()

@move_log_router.get("", response_class=HTMLResponse)
async def move_log(cls: MoveLogView = Depends()):
    """Список перемещений"""
    template = f'widgets/list.html'
    return await render(cls.r, template, context={'cls': cls})

@move_log_router.get("/line", response_class=HTMLResponse)
async def move_log_line(move_log_id: UUID, move_log_view: MoveLogView = Depends()):
    """Отдает лайну для монитора склада"""
    move_log = await move_log_view.get_lines(ids=[move_log_id])
    return await render(move_log_view.r, 'inventory/move_log/move_log_line.html', context={'move_log': move_log})


@move_log_router.get("/table", response_class=HTMLResponse)
async def move_log_line(move_log_view: MoveLogView = Depends(), order_id: UUID=None, move_id=None):
    """Отдает лайну для монитора склада"""
    if order_id:
        await move_log_view.init(params={'order_id__in': [order_id]})
    return await render(move_log_view.r, 'inventory/move_log/move_log_table.html', context={'move_logs': move_log_view})


