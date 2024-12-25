from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi import Request
from fastapi.responses import HTMLResponse

from app.front.apps.inventory.common_depends import get_user_store
from app.front.apps.inventory.views import QuantView, StoreStaffView, QuantView, LocationView
from app.front.template_spec import templates
from app.front.utills import render, convert_query_params_to_dict
from app.inventory.location.enums import PhysicalLocationClass
from core.frontend.constructor import ClassView

quant_router = APIRouter()


@quant_router.get("/quants", response_class=HTMLResponse)
async def quant_list(quants: QuantView = Depends(), zones: LocationView = Depends(),
                     store_user: StoreStaffView = Depends(get_user_store)):
    # Отчет по остаткам
    filter = {'location_class__in': list(PhysicalLocationClass)}
    filter.update(quants.r.query_params)
    await quants.init(params=filter)
    await zones.init(params={'location_class__in': ['zone']})
    return await render(
        quants.r, 'inventory/stock_reports/quant/quants.html',
        context={
            'quants': quants,
            'classes': PhysicalLocationClass,
            'zones': zones,
            'store_user': store_user
        }
    )


@quant_router.get("/quants/lines", response_class=HTMLResponse)
async def quant_lines(quants: QuantView = Depends(), store_user: StoreStaffView = Depends(get_user_store)):
    # Отчет по остаткам
    filter = {'location_class__in': list(PhysicalLocationClass)}
    filter.update(convert_query_params_to_dict(quants.r.query_params))
    await quants.init(params=filter)
    return await render(
        quants.r, 'inventory/stock_reports/quant/quant_lines.html',
        context={
            'quants': quants,
            'classes': PhysicalLocationClass,
            'store_user': store_user
        }
    )

@quant_router.get("/quants/deep_tree", response_class=HTMLResponse)
async def quant_deep_tree(quants: QuantView = Depends(), store_user: StoreStaffView = Depends(get_user_store)):
    # Отчет по остаткам
    filter = {'location_class__in': list(PhysicalLocationClass)}
    filter.update(convert_query_params_to_dict(quants.r.query_params))
    await quants.init(params=filter)
    return await render(
        quants.r, 'inventory/quant/deep_tree.html',
        context={
            'quants': quants,
            'classes': PhysicalLocationClass,
            'store_user': store_user
        }
    )