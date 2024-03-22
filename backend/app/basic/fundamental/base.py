import base64

from babel.core import LOCALE_ALIASES
from fastapi import APIRouter, Depends, HTTPException
from fastapi import Response, Request
from pydantic import BaseModel

from app.basic.fundamental.schemas.dundamental_shemas import Image
from core.helpers.s3.s3 import s3_client
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

@fundamental_router.post("/upload_image_test")
def upload(request: Request, schema: Image):
    image_as_bytes = str.encode(schema.file_data)  # convert string to bytes
    img_recovered = base64.b64decode(image_as_bytes)  # decode base64string
    with open("uploaded_" + schema.filename, "wb") as f:
        f.write(img_recovered)
    return {"message": f"Successfuly uploaded {schema.filename}"}

@fundamental_router.get("/country", response_model=list[CountrySchema])
async def countries(request: Request):
    currencies = [
        {
            'code': k, 'name': v
        } for k, v in TypeLocale(request.user.locale).territories._data.items()
    ]
    return currencies


@fundamental_router.get("/country/{code}", response_model=CountrySchema)
async def countries_code(request: Request, code: str):
    try:
        country = request.user.locale.territories._data[code.upper()]
    except KeyError as ex:
        raise HTTPException(
            status_code=404,
            detail=f"Country {str(ex)} not found"
        )
    return {'name': country, 'code': code}


@fundamental_router.get("/currency", response_model=list[CurrencySchema])
async def currencies(request: Request):
    currencies = [{'code': k, 'name': v} for k, v in TypeLocale(request.user.locale).currencies._data.items()]
    return currencies


@fundamental_router.get("/currency/{code}", response_model=CurrencySchema)
async def currencies_code(request: Request, code: str):
    try:
        currency = request.user.locale.currencies._data[code.upper()]
    except KeyError as ex:
        raise HTTPException(
            status_code=404,
            detail=f"currency {str(ex)} not found"
        )
    return {'name': currency, 'code': code}


@fundamental_router.get("/locale", response_model=list[LocaleSchema])
async def locales(request: Request):
    l = TypeLocale('en', 'US')
    locales = [TypeLocale(i) for i in LOCALE_ALIASES]
    return [i.validate(i) for i in locales]


@fundamental_router.get("/locale/my", response_model=LocaleSchema)
async def locales_my(request: Request):
    locale = TypeLocale(str(request.user.locale))
    return locale.validate(locale)


@fundamental_router.get("/locale/{code}", response_model=LocaleSchema)
async def locales_code(request: Request, code: str):
    try:
        locale = TypeLocale(code.lower())
    except UnknownLocaleError as ex:
        raise HTTPException(
            status_code=404,
            detail=str(ex)
        )
    return locale.validate(locale)
