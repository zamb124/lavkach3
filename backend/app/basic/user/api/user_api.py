import json
import uuid

import starlette
from fastapi import APIRouter, Depends, Query
from fastapi_filter import FilterDepends
from starlette.requests import Request

from app.basic.user.schemas import (
    ExceptionResponseSchema,
    UserScheme,
    UserCreateScheme,
    UserUpdateScheme,
    LoginResponseSchema,
    UserFilter,
    UserListSchema
)
from app.basic.user.services import UserService
from core.fastapi.dependencies import (
    PermissionDependency,
    IsAuthenticated,
)
from .schemas import LoginRequest
from ..schemas.user_schemas import SignUpScheme, ChangeCompanyScheme
from fastapi import Response

user_router = APIRouter()


@user_router.get("", response_model=UserListSchema, dependencies=[Depends(PermissionDependency([IsAuthenticated]))])
async def user_list(
        request: Request,
        model_filter: UserFilter = FilterDepends(UserFilter),
        size: int = Query(ge=1, le=100, default=100),
):
    data = await UserService(request).list(model_filter, size)
    if data:
        a = sorted(data, key=lambda x: x.lsn, reverse=True)
        cursor = a[0].lsn
    else:
        cursor = model_filter.lsn__gt
    return {'size': len(data), 'cursor': cursor, 'data': data}


@user_router.post(
    "",
    response_model=UserScheme,
    responses={"400": {"model": ExceptionResponseSchema}},
    dependencies=[Depends(PermissionDependency([IsAuthenticated]))]
)
async def create_user(request: Request, shema: UserCreateScheme):
    user = await UserService(request).create(shema)
    return user


@user_router.get("/{user_id}", response_model=UserScheme, dependencies=[Depends(PermissionDependency([IsAuthenticated]))])
async def user_get(request: Request, user_id: uuid.UUID):
    user = await UserService(request).get(id=user_id)
    return user

@user_router.put("/{user_id}", response_model=UserScheme,
                 dependencies=[Depends(PermissionDependency([IsAuthenticated]))])
async def user_update(request: Request, user_id: uuid.UUID, schema: UserUpdateScheme):
    return await UserService(request).update(id=user_id, obj=schema)


@user_router.delete("/{user_id}", dependencies=[Depends(PermissionDependency([IsAuthenticated]))])
async def user_delete(request: Request, user_id: uuid.UUID):
    await UserService(request).delete(id=user_id)


@user_router.post(
    "/login",
    response_model=LoginResponseSchema,
    responses={"404": {"model": ExceptionResponseSchema}},
)
async def login(request: Request, obj: LoginRequest, response: Response):
    a = await UserService(request).login(
        email=obj.email,
        password=obj.password,
    )
    response.set_cookie(key='token', value='helloworld', httponly=True)
    return a

@user_router.post("/signup", response_model=LoginResponseSchema)
async def signup(request: Request, schema: SignUpScheme):
    return await UserService(request).signup(obj=schema)


@user_router.post("/company_change", response_model=UserScheme)
async def company_change(request: Request, schema: ChangeCompanyScheme):
    return await UserService(request).company_change(schema)

