from typing import List, Union
import uuid
from fastapi import APIRouter, Depends, Query
from app.maintenance.schemas import ModelCreateScheme, ExceptionResponseSchema, ModelScheme, ModelUpdateScheme

model_router = APIRouter()

@model_router.post(
    "",
    response_model=List[ModelScheme],
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def get_model_list(limit: int = Query(10, description="Limit")):
    return await ModelScheme.get_all(limit=limit)

@model_router.get(
    "/{model_id}",
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def load_model(model_id: uuid.UUID) -> Union[None, ModelScheme]:
    return await ModelScheme.get_by_id(id=model_id)
@model_router.post(
    "/create",
    response_model=ModelScheme,
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def create_model(request: ModelCreateScheme):
    entity = await request.create()
    return entity

@model_router.put(
    "/{model_id}",
    response_model=ModelScheme,
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def update_model(model_id: uuid.UUID, request: ModelUpdateScheme):
    entity = await request.update(id=model_id)
    return entity

@model_router.delete(
    "/{model_id}",
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def update_model(model_id: uuid.UUID):
    await ModelScheme.delete_by_id(id=model_id)
