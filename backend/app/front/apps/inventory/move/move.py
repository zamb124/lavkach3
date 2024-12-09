from typing import Optional, Callable
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from mypy.dmypy.client import request

from app.front.apps.inventory.common_depends import get_user_store
from app.front.apps.inventory.views import MoveView, StoreStaffView, LocationView
from app.front.template_spec import templates
from app.front.utills import render, convert_query_params_to_dict
from app.inventory.location.enums import LocationClass

move_router = APIRouter()


@move_router.get("", response_class=HTMLResponse)
async def move_list(moves: MoveView = Depends(), zones: LocationView = Depends(),
                    store_user: StoreStaffView = Depends(get_user_store)):
    # Отчет по остаткам
    filter = {'location_class__in': list(LocationClass)}
    filter.update(moves.r.query_params)
    await moves.init(params=filter)
    await zones.init(params={'location_class__in': ['zone']})
    return render(
        moves.r, 'inventory/move/move.html',
        context={
            'moves': moves,
            'classes': LocationClass,
            'zones': zones,
            'store_user': store_user
        }
    )

@move_router.get("/line", response_class=HTMLResponse)
async def move_line(move_id: UUID, move_view: MoveView = Depends()):
    """Отдает лайну для монитора склада"""
    move = await move_view.get_lines(ids=[move_id])
    return render(move_view.r, 'inventory/move/move_line.html', context={'move': move})


@move_router.get("/detail", response_class=HTMLResponse)
async def move_detail(
        move_id: Optional[UUID] = None,
        edit: bool = False,
        create: bool = False,
        move: MoveView = Depends(),
        store_user: StoreStaffView = Depends(get_user_store),
):
    """Отдает лайну для монитора склада"""
    filter = {'store_id__in': [store_user.store_id.val], 'id__in': [move_id]}
    filter.update(convert_query_params_to_dict(move.r.query_params))
    if not create:
        await move.init(params=filter)
    else:
            move.store_id.val = store_user.store_id.val
    return render(
        move.r, 'inventory/move/move_detail.html',
        context={
            'move': move,
            'store_user': store_user,
            'edit': edit,
            'create': create,
        }
    )



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

@move_router.post("/confirm", response_class=HTMLResponse)
async def confirm(moves: MoveView = Depends(), store_user: StoreStaffView = Depends(get_user_store)):
    # Отчет по остаткам
    data: dict = await moves.r.json()
    func: Callable = getattr(moves.v.model.adapter, 'action_move_confirm')
    for move_id in data.values():
        await func(payload={'id': move_id})
    return {
        "status": "OK",
        "detail": "Move is confirmed"
    }