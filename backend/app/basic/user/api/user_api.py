from typing import List

from fastapi import APIRouter, Depends, Query
from fastapi_filter import FilterDepends
from sqlalchemy import update, select
from starlette.requests import Request

from app.basic.user.models import User
from core.db import session

from starlette.exceptions import HTTPException
from .schemas import LoginRequest
from app.basic.user.schemas import (
    ExceptionResponseSchema,
    UserScheme,
    UserCreateScheme,
    LoginResponseSchema,
    UserFilter,
    UserListSchema
)
from app.basic.user.services import UserService
from core.integration.wms import ClientWMS
from core.fastapi.dependencies import (
    PermissionDependency,
    IsAuthenticated,
)

user_router = APIRouter()

@user_router.get("", response_model=UserListSchema)
async def company_list(
        request: Request,
        model_filter: UserFilter = FilterDepends(UserFilter),
        size: int = Query(ge=1, le=100, default=100),
):
    data = await UserService(request).list(model_filter, size)
    cursor = model_filter.lsn__gt
    return {'size': len(data), 'cursor': cursor, 'data': data}

@user_router.post(
    "",
    response_model=UserScheme,
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def create_user(request: Request, shema: UserCreateScheme):
    user =  await UserService(request).create(shema)
    return user


@user_router.post(
    "/login",
    response_model=LoginResponseSchema,
    responses={"404": {"model": ExceptionResponseSchema}},
)
async def login(request: Request, obj: LoginRequest):
    return await UserService(request).login(
        email=obj.email,
        password=obj.password,
    )


@user_router.get(
    "/{barcode}",
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def search_barcode(request:Request, barcode: str):

    response = await ClientWMS.assign_device(
        barcode=barcode,
        path='/api/tsd/user/assign_device',
    )
    if response is None:
        raise HTTPException(status_code=429, detail='Try later')
    if isinstance(response, int):
        raise HTTPException(status_code=response, detail='oh No')

    user = UserScheme(
        password1=response['token'],
        store_id=response['store_id'],
        password2=response['token'],
        nickname=response['fullname'],
        email=f'{response["fullname"]}@yandex.ru',
    )
    try:
        our_user = await UserService(request).create_user(**user.dict())
    except Exception:
        # TODO заменить здесь email на стор
        query = (
            update(User)
            .where(User.nickname == response['fullname'])
            .values({'store_id': response['store_id']})
        )
        await session.execute(query)
        await session.commit()
        query = (
            select(User)
            .where(User.nickname == response['fullname'])
        )
        result = await session.execute(query)
        our_user = result.scalars().first()

    return our_user
