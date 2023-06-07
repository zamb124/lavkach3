from typing import List

from fastapi import APIRouter, Depends, Query
from app.store.schemas import (
    StoreSchema,
    ExceptionResponseSchema
)

store_router = APIRouter()

@store_router.get(
    "",
    response_model=list[StoreSchema],
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def get_company_list(limit: int = Query(10, description="Limit")):
    print('lol')
    a= await StoreSchema.get_all(limit=limit)
    return a

@store_router.post(
    "",
    response_model=StoreSchema,
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def create_company(request: StoreSchema):
    res = await request.create()
    return await request.get_by_id(res)
