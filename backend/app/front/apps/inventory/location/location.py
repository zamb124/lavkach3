from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi import Request
from fastapi.responses import HTMLResponse
from starlette.responses import JSONResponse

from app.front.apps.inventory.common_depends import get_user_store
from app.front.apps.inventory.views import LocationView, StoreStaffView, QuantView
from app.front.template_spec import templates
from app.front.utills import render, convert_query_params_to_dict
from app.inventory.location.enums import LocationClass
from app.inventory.location.schemas import UpdateParent
from core.frontend.constructor import ClassView

location_router = APIRouter()


@location_router.get("", response_class=HTMLResponse)
async def location_list(request: Request, store_user: StoreStaffView = Depends(get_user_store)):
    # Отчет по остаткам
    locations = LocationView(request)
    zones = LocationView(request)
    filter = {'store_id__in': [store_user.store_id.val]}
    filter.update(convert_query_params_to_dict(locations.r.query_params))
    await locations.init(params=filter)
    await zones.init(params={'location_class__in': ['zone'], 'store_id__in': [store_user.store_id.val]})
    return render(
        locations.r, 'inventory/location/location.html',
        context={
            'locations': locations,
            'classes': LocationClass,
            'zones': zones,
            'store_user': store_user,
            'scroll': True
        }
    )


@location_router.get("/lines", response_class=HTMLResponse)
async def location_lines(request: Request, store_user: StoreStaffView = Depends(get_user_store), scroll: bool = False):
    # Отчет по остаткам

    locations = LocationView(request)
    filter = {'store_id__in': [store_user.store_id.val]}
    filter.update(convert_query_params_to_dict(locations.r.query_params))
    await locations.init(params=filter)
    return render(
        locations.r, 'inventory/location/location_lines.html',
        context={
            'locations': locations,
            'store_user': store_user,
            'scroll': scroll
        }
    )

@location_router.get("/detail", response_class=HTMLResponse)
async def location_detail(
        request: Request,
        location_id: UUID,
        edit: bool = False,
        store_user: StoreStaffView = Depends(get_user_store),

):
    location = LocationView(request)
    quants = QuantView(request)
    filter = {'store_id__in': [store_user.store_id.val], 'id__in': [location_id]}
    filter.update(convert_query_params_to_dict(location.r.query_params))
    await location.init(params=filter)
    await quants.init(params={'location_id__in': [location._id]})
    async with location.v.model.adapter as a:
        location_tree = await a.get_location_tree({'location_ids': [location_id]})
    return render(
        location.r, 'inventory/location/location_detail.html',
        context={
            'location': location,
            'store_user': store_user,
            'quants': quants,
            'edit': edit,
            'location_tree': location_tree
        }
    )

@location_router.post("/detail", response_class=HTMLResponse)  # type: ignore
async def location_detail(
        request: Request,
        location_id: UUID,
        store_user: StoreStaffView = Depends(get_user_store),

):
    location = LocationView(request)
    quants = QuantView(request)
    filter = {'store_id__in': [store_user.store_id.val], 'id__in': [location_id]}
    filter.update(convert_query_params_to_dict(location.r.query_params))
    data = await request.json()
    async with request.scope['env']['location'].adapter as a:
        origin_location = await a.get(location_id)
        if origin_location:
            origin_location.update(data)
            updated_location = await a.update(location_id, origin_location)
    await location.init(params=filter, data=[updated_location])
    await quants.init(params={'location_id__in': [location._id]})
    return render(
        location.r, 'inventory/location/location_detail.html',
        context={
            'location': location,
            'store_user': store_user,
            'quants': quants,
            'edit': False
        }
    )

@location_router.post("/update_parent", response_class=HTMLResponse)  # type: ignore
async def update_parent(
        request: Request,
        schema: UpdateParent
):
    async with request.scope['env']['location'].adapter as a:
        origin_location = await a.location_update_parent({'id': schema.id, 'parent_id': schema.parent_id})
    return JSONResponse({'status': 'ok'})