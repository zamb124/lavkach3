import uuid

from fastapi import APIRouter, Query, Depends
from fastapi_filter import FilterDepends
from starlette.requests import Request

from app.basic.partner.schemas import (
    PartnerScheme,
    PartnerCreateScheme,
    PartnerUpdateScheme,
    ExceptionResponseSchema, PartnerListSchema, PartnerFilter
)
from app.basic.partner.services import PartnerService

partner_router = APIRouter(
    # dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
    responses={"400": {"model": ExceptionResponseSchema}},
)


@partner_router.get("", response_model=PartnerListSchema)
async def partner_list(
        model_filter: PartnerFilter = FilterDepends(PartnerFilter),
        size: int = Query(ge=1, le=100, default=100),
        service: PartnerService = Depends()
):
    data = await service.list(model_filter, size)
    cursor = model_filter.lsn__gt
    return {'size': len(data), 'cursor': cursor, 'data': data}


@partner_router.post("", response_model=PartnerScheme)
async def partner_create(schema: PartnerCreateScheme, service: PartnerService = Depends()):
    return await service.create(obj=schema)


@partner_router.get("/{partner_id}")
async def partner_get(partner_id: uuid.UUID, service: PartnerService = Depends()):
    return await service.get(id=partner_id)


@partner_router.put("/{partner_id}", response_model=PartnerScheme)
async def partner_update(partner_id: uuid.UUID, schema: PartnerUpdateScheme, service: PartnerService = Depends()):
    return await service.update(id=partner_id, obj=schema)


@partner_router.delete("/{partner_id}")
async def partner_delete(partner_id: uuid.UUID, service: PartnerService = Depends()):
    await service.delete(id=partner_id)
