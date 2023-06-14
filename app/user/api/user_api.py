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
    UserScheme,
    UserCreateScheme,
    UserUpdateScheme,
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
    response_model=List[UserScheme],
    response_model_exclude={"id"},
    responses={"400": {"model": ExceptionResponseSchema}},
   # dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
)
async def get_user_list(
        limit: int = Query(10, description="Limit"),
        cursor: int = Query(0, description="Cursor"),
):
    return await UserService().list(limit=limit, cursor=cursor)


@user_router.post(
    "",
    response_model=UserScheme,
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def create_user(request: UserCreateScheme):
    user =  await UserService().create(request)
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

    user = UserScheme(
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
