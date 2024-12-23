from email.policy import default
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi import Request
from fastapi.responses import HTMLResponse
from mypy.checkexpr import defaultdict
from starlette.responses import JSONResponse

from app.front.apps.inventory.common_depends import get_user_store
from app.front.apps.inventory.views import LocationView, StoreStaffView, QuantView, LocationTreeView
from app.front.template_spec import templates
from app.front.utills import render, convert_query_params_to_dict
from app.inventory.location.enums import LocationClass, PhysicalLocationClass, PhysicalStoreLocationClass
from app.inventory.location.schemas import UpdateParent, GetLocationTreeSchema, LocationTreeSchema
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


@location_router.get("/zones", response_class=HTMLResponse)
async def location_list_zones(request: Request, store_user: StoreStaffView = Depends(get_user_store)):
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
        location_id: Optional[UUID] = None,
        edit: bool = False,
        create: bool = False,
        store_user: StoreStaffView = Depends(get_user_store),

):
    location = LocationView(request)
    quants = QuantView(request)
    filter = {'store_id__in': [store_user.store_id.val], 'id__in': [location_id]}
    filter.update(convert_query_params_to_dict(location.r.query_params))
    location_tree = []
    if not create:
        await location.init(params=filter)
        await quants.init(params={'location_id__in': [location._id]})
        async with location.v.model.adapter as a:
            location_tree = await a.get_location_tree({'location_ids': [location_id]})
    else:
        location.store_id.val = store_user.store_id.val
        location.location_class.val = LocationClass.PLACE
    return render(
        location.r, 'inventory/location/location_detail.html',
        context={
            'location': location,
            'store_user': store_user,
            'quants': quants,
            'edit': edit,
            'create': create,
            'location_tree': location_tree
        }
    )


@location_router.post("/detail", response_class=HTMLResponse)  # type: ignore
async def location_detail(
        request: Request,
        location_id: Optional[UUID | int],
        store_user: StoreStaffView = Depends(get_user_store),

):
    location = LocationView(request)
    quants = QuantView(request)
    data = await request.json()
    if isinstance(location_id, int):
        location = await location.create_line(data)
    else:
        location = await location.update_line(location_id, data)
    filter = {'store_id__in': [store_user.store_id.val], 'id__in': [location._id]}
    filter.update(convert_query_params_to_dict(location.r.query_params))
    await quants.init(params={'location_id__in': [location._id]})
    location_tree = []
    async with location.v.model.adapter as a:
        location_tree = await a.get_location_tree({'location_ids': [location_id]})
    return render(
        location.r, 'inventory/location/location_detail.html',
        context={
            'location': location,
            'store_user': store_user,
            'quants': quants,
            'edit': False,
            'location_tree': location_tree
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


@location_router.get("/map", response_class=HTMLResponse)
async def location_map(request: Request, store_user: StoreStaffView = Depends(get_user_store)):
    # Карта локаций склада
    zones = LocationView(request)
    await zones.init(
        params={
            'location_id__isnull': True,
            'store_id__in': [store_user.store_id.val],
            'location_class__in': list(PhysicalStoreLocationClass)
        })
    async with zones.v.model.adapter as a:
        locations = await a.get_location_tree({'location_ids': [i._id for i in zones]})
    return render(
        zones.r, 'inventory/location/map.html',
        context={
            'locations': locations,
            'zones': zones,
            'store_user': store_user,
        }
    )


def flatten_location_tree(location_tree):
    location_dict = {}

    def extract_locations(location):
        location_dict[location['id']] = location
        for child in location.get('child_locations_rel', []):
            extract_locations(child)

    for location in location_tree:
        extract_locations(location)

    return location_dict


@location_router.put("/deep_tree", response_class=HTMLResponse)
async def location_deep_tree(request: Request, location_id: UUID, store_user: StoreStaffView = Depends(get_user_store)):
    # Глубока Карта локации, с квантами
    # где каждой локации приклеивается так же список квантов
    location = LocationTreeView(request)
    async with location.v.model.adapter as a:
        location_tree = await a.get_location_tree({
            'location_ids': [location_id],
            'deep': True
        })
    await location.init(data=location_tree)
    return render(
        location.r, 'inventory/location/location_tree.html',
        context={
            'location_tree': location,
            'store_user': store_user,
            'deep': True,
        }
    )
