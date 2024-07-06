import uuid

from fastapi import APIRouter, Depends, Query, BackgroundTasks
from fastapi import Response
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
from ...bus.managers import ws_manager

user_router = APIRouter()


@user_router.get("", response_model=UserListSchema, dependencies=[Depends(PermissionDependency([IsAuthenticated]))])
async def user_list(
        model_filter: UserFilter = FilterDepends(UserFilter),
        size: int = Query(ge=1, le=100, default=100),
        service: UserService = Depends()
):
    data = await service.list(model_filter, size)
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
async def create_user(schema: UserCreateScheme, service: UserService = Depends()):
    user = await service.create(schema)
    return user


@user_router.get("/{user_id}", response_model=UserScheme, dependencies=[Depends(PermissionDependency([IsAuthenticated]))])
async def user_get(user_id: uuid.UUID, service: UserService = Depends()):
    user = await service.get(id=user_id)
    return user


@user_router.put("/{user_id}", response_model=UserScheme,dependencies=[Depends(PermissionDependency([IsAuthenticated]))])
async def user_update(user_id: uuid.UUID, schema: UserUpdateScheme, service: UserService = Depends()):
    return await service.update(id=user_id, obj=schema)


@user_router.delete("/{user_id}", dependencies=[Depends(PermissionDependency([IsAuthenticated]))])
async def user_delete(user_id: uuid.UUID, service: UserService = Depends()):
    await service.delete(id=user_id)


@user_router.post(
    "/login",
    response_model=LoginResponseSchema,
    responses={"404": {"model": ExceptionResponseSchema}},
)
async def login(schema: LoginRequest, service: UserService = Depends()):
    return await service.login(
        email=schema.email,
        password=schema.password,
    )


@user_router.post("/signup", response_model=LoginResponseSchema)
async def signup(schema: SignUpScheme, service: UserService = Depends()):
    return await service.signup(obj=schema)


@user_router.post(
    "/refresh",
    response_model=LoginResponseSchema,
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def refresh_token(service: UserService = Depends()):
    return await service.login(user=service.user)


async def send_ws_company_changed(user_id):
    a = await ws_manager.send_personal_message(
        message='Company was changed',
        user_id=user_id,
        message_type='COMPANY_CHANGED'
    )


@user_router.post("/company_change", response_model=UserScheme)
async def company_change(schema: ChangeCompanyScheme, background_tasks: BackgroundTasks, service: UserService = Depends()):
    res = await service.company_change(schema)
    background_tasks.add_task(send_ws_company_changed, res.id)
    return res


@user_router.get("/{user_id}/permissions", response_model=list[str],
                 dependencies=[Depends(PermissionDependency([IsAuthenticated]))])
async def permissions(user_id: uuid.UUID, service: UserService = Depends()):
    return await service.permissions(user_id=user_id)
