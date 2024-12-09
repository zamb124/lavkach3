from collections import defaultdict
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse

from app.front.apps.inventory.common_depends import get_user_store
from app.front.apps.inventory.views import QuantView, LocationView, StoreStaffView, MoveView
from app.front.template_spec import templates
from app.front.utills import render, convert_query_params_to_dict
from app.inventory.location.enums import PhysicalLocationClass, LocationClass

stocks_reports_router = APIRouter()




@stocks_reports_router.get("/quants", response_class=HTMLResponse)
async def quant_list(quants: QuantView = Depends(), zones: LocationView = Depends(),
                     store_user: StoreStaffView = Depends(get_user_store)):
    # Отчет по остаткам
    filter = {'location_class__in': list(PhysicalLocationClass)}
    filter.update(quants.r.query_params)
    await quants.init(params=filter)
    await zones.init(params={'location_class__in': ['zone']})
    return render(
        quants.r, 'inventory/stock_reports/quant/quants.html',
        context={
            'quants': quants,
            'classes': PhysicalLocationClass,
            'zones': zones,
            'store_user': store_user
        }
    )


@stocks_reports_router.get("/quants/lines", response_class=HTMLResponse)
async def quant_lines(quants: QuantView = Depends(), store_user: StoreStaffView = Depends(get_user_store)):
    # Отчет по остаткам
    filter = {'location_class__in': list(PhysicalLocationClass)}
    filter.update(convert_query_params_to_dict(quants.r.query_params))
    await quants.init(params=filter)
    return render(
        quants.r, 'inventory/stock_reports/quant/quant_lines.html',
        context={
            'quants': quants,
            'classes': PhysicalLocationClass,
            'store_user': store_user
        }
    )


@stocks_reports_router.get("/moves", response_class=HTMLResponse)
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

