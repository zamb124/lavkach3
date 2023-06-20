import uuid
import typing
from app.basic.partner.schemas import (
    PartnerScheme,
    PartnerCreateScheme,
    PartnerUpdateScheme,
    ExceptionResponseSchema
)
from app.basic.partner.services import PartnerService
from fastapi import APIRouter, Query

partner_router = APIRouter(
    #dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
    responses={"400": {"model": ExceptionResponseSchema}},
)


@partner_router.get("", response_model=list[PartnerScheme])
async def partner_list(
        limit: int = Query(10, description="Limit"),
        cursor: int = Query(0, description="Cursor"),
):
    return await PartnerService().list(limit, cursor)


@partner_router.post("/create", response_model=PartnerScheme)
async def create_partner(request: PartnerCreateScheme):
    return await PartnerService().create(obj=request)


@partner_router.get("/{partner_id}")
async def load_partner(partner_id: uuid.UUID) -> PartnerScheme:
    return await PartnerService().get(id=partner_id)


@partner_router.put("/{partner_id}",response_model=PartnerScheme)
async def update_partner(partner_id: uuid.UUID, request: PartnerUpdateScheme):
    return await PartnerService().update(id=partner_id, obj=request)


@partner_router.delete("/{partner_id}")
async def delete_partner(partner_id: uuid.UUID):
    await PartnerService().delete(id=partner_id)
