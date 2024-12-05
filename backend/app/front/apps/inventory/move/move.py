from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse

from app.front.apps.inventory.common_depends import get_user_store
from app.front.apps.inventory.views import MoveView, StoreStaffView
from app.front.template_spec import templates
from app.front.utills import render, convert_query_params_to_dict

move_router = APIRouter()

@move_router.get("", response_class=HTMLResponse)
async def move(cls: MoveView = Depends()):
    """Список перемещений"""
    template = f'widgets/list{"" if cls.r.scope["htmx"].hx_request else "-full"}.html'
    return templates.TemplateResponse(cls.r, template, context={'cls': cls})



@move_router.get("/line", response_class=HTMLResponse)
async def move_line(move_id: UUID, move_view: MoveView = Depends()):
    """Отдает лайну для монитора склада"""
    move = await move_view.get_lines(ids=[move_id])
    return render(move_view.r, 'inventory/move/move_line.html', context={'move': move})


@move_router.get("/detail", response_class=HTMLResponse)
async def move_detail(move_id: UUID, move_view: MoveView = Depends()):
    """Отдает лайну для монитора склада"""
    move = await move_view.get_lines(ids=[move_id])
    return render(move_view.r, 'inventory/move/move_detail.html', context={'move': move})


@move_router.get("/lines", response_class=HTMLResponse)
async def move_lines(moves: MoveView = Depends(), store_user: StoreStaffView = Depends(get_user_store)):
    # Отчет по остаткам
    filter = (convert_query_params_to_dict(moves.r.query_params))
    await moves.init(params=filter)
    return render(
        moves.r, 'inventory/move/move_lines.html',
        context={
            'moves': moves,
            'store_user': store_user
        }
    )