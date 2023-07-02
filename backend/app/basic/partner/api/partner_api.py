import uuid
import typing

from starlette.requests import Request

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
        request: Request,
        limit: int = Query(10, description="Limit"),
        cursor: int = Query(0, description="Cursor"),
):
    return await PartnerService(request).list(limit, cursor)


@partner_router.post("/create", response_model=PartnerScheme)
async def create_partner(request: Request, schema: PartnerCreateScheme):
    return await PartnerService(request).create(obj=schema)


@partner_router.get("/{partner_id}")
async def load_partner(request: Request, partner_id: uuid.UUID) -> PartnerScheme:
    return await PartnerService(request).get(id=partner_id)


@partner_router.put("/{partner_id}",response_model=PartnerScheme)
async def update_partner(request: Request, partner_id: uuid.UUID, schema: PartnerUpdateScheme):
    return await PartnerService(request).update(id=partner_id, obj=schema)


@partner_router.delete("/{partner_id}")
async def delete_partner(request: Request, partner_id: uuid.UUID):
    await PartnerService(request).delete(id=partner_id)
