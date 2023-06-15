from fastapi import APIRouter, Depends, HTTPException
from fastapi import Response, Request
from pydantic import BaseModel
import json
from core.fastapi.dependencies import AllowAll

from core.fastapi.dependencies import (
    PermissionDependency,
    IsAuthenticated,
)
from core.schemas.basic_schemes import CurrencySchema, CountrySchema, LocaleSchema, PhoneSchema


class ExceptionResponseSchema(BaseModel):
    error: str

base_router = APIRouter(
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
    responses={"400": {"model": ExceptionResponseSchema}},
)

@base_router.get("/health", dependencies=[Depends(PermissionDependency([AllowAll]))])
async def health():
    return Response(status_code=200)

@base_router.get("/countries", response_model=list[CountrySchema])
async def countries(request: Request):
    user_data = await request.user.get_user_data()
    currencies = [{'code':k,'name': v} for k, v in user_data.locale.territories._data.items()]
    return currencies

@base_router.get("/countries/{code}", response_model=CountrySchema)
async def countries_code(request: Request, code: str):
    user_data = await request.user.get_user_data()
    try:
        country = user_data.locale.territories._data[code.upper()]
    except KeyError as ex:
        raise HTTPException(
            status_code=404,
            detail=f"Country {str(ex)} not found"
        )
    return {'name':country, 'code': code}

@base_router.get("/currencies", response_model=list[CurrencySchema])
async def currencies(request: Request):
    user_data = await request.user.get_user_data()
    currencies = [{'code':k,'name': v} for k, v in user_data.locale.currencies._data.items()]
    return currencies

@base_router.get("/currencies/{code}", response_model=CurrencySchema)
async def currencies_code(request: Request, code: str):
    user_data = await request.user.get_user_data()
    try:
        currency = user_data.locale.currencies._data[code.upper()]
    except KeyError as ex:
        raise HTTPException(
            status_code=404,
            detail=f"Country {str(ex)} not found"
        )
    return {'name':currency, 'code': code}