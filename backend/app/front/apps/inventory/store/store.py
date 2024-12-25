from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi import Request
from fastapi.responses import HTMLResponse

from app.front.apps.inventory.common_depends import get_user_store
from app.front.apps.inventory.views import StoreView, StoreStaffView, QuantView, LocationView
from app.front.template_spec import templates
from app.front.utills import render, convert_query_params_to_dict
from core.frontend.constructor import ClassView

store_router = APIRouter()


@store_router.get("", response_class=HTMLResponse)
async def store_list(request: Request, store_user: StoreStaffView = Depends(get_user_store)):
    # Отчет по остаткам
    stores = StoreView(request)
    filter = {}
    filter.update(convert_query_params_to_dict(stores.r.query_params))
    await stores.init(params=filter)
    return await render(
        stores.r, 'inventory/store/store.html',
        context={
            'stores': stores,
            'store_user': store_user,
            'scroll': True
        }
    )


@store_router.get("/lines", response_class=HTMLResponse)
async def store_lines(request: Request, store_user: StoreStaffView = Depends(get_user_store), scroll: bool = False):
    # Отчет по остаткам

    stores = StoreView(request)
    filter = {}
    filter.update(convert_query_params_to_dict(stores.r.query_params))
    await stores.init(params=filter)
    return await render(
        stores.r, 'inventory/store/store_lines.html',
        context={
            'stores': stores,
            'store_user': store_user,
            'scroll': scroll
        }
    )

@store_router.get("/detail", response_class=HTMLResponse)
async def store_detail(
        request: Request,
        store_id: UUID,
        edit: bool = False,
        store_user: StoreStaffView = Depends(get_user_store),

):
    store = StoreView(request)
    quants = QuantView(request)
    filter = {'id': store_id}
    filter.update(convert_query_params_to_dict(store.r.query_params))
    await store.init(params=filter)
    await quants.init(params={'store_id__in': [store._id]})

    return await render(
        store.r, 'inventory/store/store_detail.html',
        context={
            'store': store,
            'store_user': store_user,
            'quants': quants,
            'edit': edit
        }
    )

@store_router.post("/detail", response_class=HTMLResponse)  # type: ignore
async def store_detail(
        request: Request,
        store_id: UUID,
        store_user: StoreStaffView = Depends(get_user_store),

):
    store = StoreView(request)
    quants = QuantView(request)
    filter = {'store_id__in': [store_user.store_id.val], 'id__in': [store_id]}
    filter.update(convert_query_params_to_dict(store.r.query_params))
    data = await request.json()
    async with request.scope['env']['store'].adapter as a:
        origin_store = await a.get(store_id)
        if origin_store:
            origin_store.update(data)
            updated_store = await a.update(store_id, origin_store)
    await store.init(params=filter, data=[updated_store])
    await quants.init(params={'store_id__in': [store._id]})
    return await render(
        store.r, 'inventory/store/store_detail.html',
        context={
            'store': store,
            'store_user': store_user,
            'quants': quants,
            'edit': False
        }
    )