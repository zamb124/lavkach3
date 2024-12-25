from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi import Request
from fastapi.responses import HTMLResponse

from app.front.apps.inventory.common_depends import get_user_store
from app.front.apps.inventory.views import OrderTypeView, StoreStaffView, QuantView, LocationView
from app.front.template_spec import templates
from app.front.utills import render, convert_query_params_to_dict
from core.frontend.constructor import ClassView

order_type_router = APIRouter()


@order_type_router.get("", response_class=HTMLResponse)
async def order_type_list(request: Request, store_user: StoreStaffView = Depends(get_user_store)):
    # Отчет по остаткам
    order_types = OrderTypeView(request)
    filter = {}
    filter.update(convert_query_params_to_dict(order_types.r.query_params))
    await order_types.init(params=filter)
    return await render(
        order_types.r, 'inventory/order_type/order_type.html',
        context={
            'order_types': order_types,
            'store_user': store_user,
            'scroll': True
        }
    )


@order_type_router.get("/lines", response_class=HTMLResponse)
async def order_type_lines(request: Request, store_user: StoreStaffView = Depends(get_user_store), scroll: bool = False):
    # Отчет по остаткам

    order_types = OrderTypeView(request)
    filter = {}
    filter.update(convert_query_params_to_dict(order_types.r.query_params))
    await order_types.init(params=filter)
    return await render(
        order_types.r, 'inventory/order_type/order_type_lines.html',
        context={
            'order_types': order_types,
            'store_user': store_user,
            'scroll': scroll
        }
    )

@order_type_router.get("/detail", response_class=HTMLResponse)
async def order_type_detail(
        request: Request,
        order_type_id: UUID,
        edit: bool = False,
        store_user: StoreStaffView = Depends(get_user_store),

):
    order_type = OrderTypeView(request)
    quants = QuantView(request)
    filter = {'id': order_type_id}
    filter.update(convert_query_params_to_dict(order_type.r.query_params))
    await order_type.init(params=filter)
    await quants.init(params={'order_type_id__in': [order_type._id]})

    return await render(
        order_type.r, 'inventory/order_type/order_type_detail.html',
        context={
            'order_type': order_type,
            'store_user': store_user,
            'quants': quants,
            'edit': edit
        }
    )

@order_type_router.post("/detail", response_class=HTMLResponse)  # type: ignore
async def order_type_detail(
        request: Request,
        order_type_id: UUID,
        store_user: StoreStaffView = Depends(get_user_store),

):
    order_type = OrderTypeView(request)
    quants = QuantView(request)
    filter = {'store_id__in': [store_user.store_id.val], 'id__in': [order_type_id]}
    filter.update(convert_query_params_to_dict(order_type.r.query_params))
    data = await request.json()
    async with request.scope['env']['order_type'].adapter as a:
        origin_order_type = await a.get(order_type_id)
        if origin_order_type:
            origin_order_type.update(data)
            updated_order_type = await a.update(order_type_id, origin_order_type)
    await order_type.init(params=filter, data=[updated_order_type])
    await quants.init(params={'order_type_id__in': [order_type._id]})
    return await render(
        order_type.r, 'inventory/order_type/order_type_detail.html',
        context={
            'order_type': order_type,
            'store_user': store_user,
            'quants': quants,
            'edit': False
        }
    )