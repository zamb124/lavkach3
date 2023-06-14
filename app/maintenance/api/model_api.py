import uuid
import typing
from fastapi import APIRouter, Query
from app.maintenance.schemas import (
    ModelScheme,
    ModelCreateScheme,
    ModelUpdateScheme,
    ExceptionResponseSchema
)
from app.maintenance.services.maintenance_service import ModelService

model_router = APIRouter()


@model_router.get(
    "",
    response_model=list[ModelScheme],
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def model_list(
        limit: int = Query(10, description="Limit"),
        cursor: int = Query(0, description="Prev LSN"),
):
    return await ModelService().list(limit, cursor)


@model_router.post(
    "/create",
    response_model=ModelScheme,
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def create_model(request: ModelCreateScheme):
    return await ModelService().create(obj=request)


@model_router.get(
    "/{model_id}",
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def load_model(model_id: uuid.UUID) -> typing.Union[None, ModelScheme]:
    return await ModelService().get(id=model_id)


@model_router.put(
    "/{model_id}",
    response_model=ModelScheme,
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def update_model(model_id: uuid.UUID, request: ModelUpdateScheme):
    return await ModelService().update(id=model_id, obj=request)


@model_router.delete(
    "/{model_id}",
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def delete_model(model_id: uuid.UUID):
    await ModelService().delete(id=model_id)
