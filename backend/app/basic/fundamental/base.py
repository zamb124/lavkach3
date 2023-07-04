from babel.core import LOCALE_ALIASES
from fastapi import APIRouter, Depends, HTTPException
from fastapi import Response, Request
from pydantic import BaseModel

from core.fastapi.dependencies import AllowAll
from core.fastapi.dependencies import (
    PermissionDependency,
    IsAuthenticated,
)
from core.schemas.basic_schemes import CurrencySchema, CountrySchema, LocaleSchema
from core.types.types import TypeLocale
from babel.core import UnknownLocaleError


class ExceptionResponseSchema(BaseModel):
    error: str


fundamental_router = APIRouter(
    responses={"400": {"model": ExceptionResponseSchema}},
)


@fundamental_router.get(
    "/health",
    #dependencies=[Depends(PermissionDependency([AllowAll]))]
)
async def health():
    return Response(status_code=200)


@fundamental_router.get("/countries", response_model=list[CountrySchema])
async def countries(request: Request):
    user_data = await request.user.get_user_data(request)
    currencies = [
        {
            'code': k, 'name': v
        } for k, v in user_data.locale.territories._data.items()
    ]
    return currencies


@fundamental_router.get("/countries/{code}", response_model=CountrySchema)
async def countries_code(request: Request, code: str):
    user_data = await request.user.get_user_data(request)
    try:
        country = user_data.locale.territories._data[code.upper()]
    except KeyError as ex:
        raise HTTPException(
            status_code=404,
            detail=f"Country {str(ex)} not found"
        )
    return {'name': country, 'code': code}


@fundamental_router.get("/currencies", response_model=list[CurrencySchema])
async def currencies(request: Request):
    user_data = await request.user.get_user_data(request)
    currencies = [{'code': k, 'name': v} for k, v in user_data.locale.currencies._data.items()]
    return currencies


@fundamental_router.get("/currencies/{code}", response_model=CurrencySchema)
async def currencies_code(request: Request, code: str):
    user_data = await request.user.get_user_data(request)
    try:
        currency = user_data.locale.currencies._data[code.upper()]
    except KeyError as ex:
        raise HTTPException(
            status_code=404,
            detail=f"currency {str(ex)} not found"
        )
    return {'name': currency, 'code': code}


@fundamental_router.get("/locales", response_model=list[LocaleSchema])
async def locales(request: Request):
    locales = [TypeLocale(i) for i in LOCALE_ALIASES]
    return [i.validate(i) for i in locales]


@fundamental_router.get("/locales/my", response_model=LocaleSchema)
async def locales_my(request: Request):
    user = await request.user.get_user_data(request)
    locale = TypeLocale(str(user.locale))
    return locale.validate(locale)


@fundamental_router.get("/locales/{code}", response_model=LocaleSchema)
async def locales_code(request: Request, code: str):
    try:
        locale = TypeLocale(code.lower())
    except UnknownLocaleError as ex:
        raise HTTPException(
            status_code=404,
            detail=str(ex)
        )
    return locale.validate(locale)
