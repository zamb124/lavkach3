import uuid
import typing

from fastapi_filter import FilterDepends
from starlette.requests import Request

from app.basic.partner.models import Partner
from app.basic.partner.schemas import (
    PartnerScheme,
    PartnerCreateScheme,
    PartnerUpdateScheme,
    ExceptionResponseSchema, PartnerListSchema, PartnerFilter
)
from app.basic.partner.services import PartnerService
from fastapi import APIRouter, Query

partner_router = APIRouter(
    # dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
    responses={"400": {"model": ExceptionResponseSchema}},
)


@partner_router.get("", response_model=PartnerListSchema)
async def partner_list(
        request: Request,
        model_filter: PartnerFilter = FilterDepends(PartnerFilter),
        size: int = Query(ge=1, le=100, default=100),
):
    data = await PartnerService(request).list(model_filter, size)
    cursor = model_filter.lsn__gt
    return {'size': len(data), 'cursor': cursor, 'data': data}


@partner_router.post("/create", response_model=PartnerScheme)
async def partner_create(request: Request, schema: PartnerCreateScheme):
    return await PartnerService(request).create(obj=schema)


@partner_router.get("/{partner_id}")
async def partner_get(request: Request, partner_id: uuid.UUID):
    return await PartnerService(request).get(id=partner_id)


@partner_router.put("/{partner_id}", response_model=PartnerScheme)
async def partner_update(request: Request, partner_id: uuid.UUID, schema: PartnerUpdateScheme):
    return await PartnerService(request).update(id=partner_id, obj=schema)


@partner_router.delete("/{partner_id}")
async def partner_delete(request: Request, partner_id: uuid.UUID):
    await PartnerService(request).delete(id=partner_id)
