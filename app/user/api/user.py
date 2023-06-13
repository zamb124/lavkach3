from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy import update, select
from app.user.models import User
from core.db import session

from starlette.exceptions import HTTPException
from .schemas import LoginRequest
from .schemas import LoginResponse
from app.user.schemas import (
    ExceptionResponseSchema,
    GetUserListResponseSchema,
    CreateUserRequestSchema,
    CreateUserResponseSchema,
)
from app.user.services import UserService
from core.integration.wms import ClientWMS
from core.fastapi.dependencies import (
    PermissionDependency,
    IsAuthenticated,
)

user_router = APIRouter()


@user_router.get(
    "",
    response_model=List[GetUserListResponseSchema],
    response_model_exclude={"id"},
    responses={"400": {"model": ExceptionResponseSchema}},
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
)
async def get_user_list(
        limit: int = Query(10, description="Limit"),
        prev: int = Query(None, description="Prev ID"),
):
    return await UserService().get_user_list(limit=limit, prev=prev)


@user_router.post(
    "",
    response_model=GetUserListResponseSchema,
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def create_user(request: CreateUserRequestSchema):
    request.password = request.password1
    #delattr(request, 'password1')
    #delattr(request, 'password2')
    user =  await UserService().create_user(
        email = request.email,
        password1=request.password1,
        password2=request.password2,
        nickname=request.nickname,
        store_id = 'f4704c92-7e14-498c-836a-72dfb3d7c6ec'
    )
    return user


@user_router.post(
    "/login",
    response_model=LoginResponse,
    responses={"404": {"model": ExceptionResponseSchema}},
)
async def login(request: LoginRequest):
    token = await UserService().login(
        email=request.email,
        password=request.password
    )
    return {"token": token.token, "refresh_token": token.refresh_token}


@user_router.get(
    "/{barcode}",
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def search_barcode(barcode: str):

    response = await ClientWMS.assign_device(
        barcode=barcode,
        path='/api/tsd/user/assign_device',
    )
    if response is None:
        raise HTTPException(status_code=429, detail='Try later')
    if isinstance(response, int):
        raise HTTPException(status_code=response, detail='oh No')

    user = CreateUserRequestSchema(
        password1=response['token'],
        store_id=response['store_id'],
        password2=response['token'],
        nickname=response['fullname'],
        email=f'{response["fullname"]}@yandex.ru',
    )
    try:
        our_user = await UserService().create_user(**user.dict())
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
