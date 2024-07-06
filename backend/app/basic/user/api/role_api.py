import uuid

from fastapi import APIRouter, Query
from fastapi_filter import FilterDepends
from starlette.requests import Request

from app.basic.user.schemas import (
    RoleScheme,
    RoleCreateScheme,
    RoleUpdateScheme,
    ExceptionResponseSchema,
    PermissionListSchema
)
from app.basic.user.schemas.role_schemas import RoleListSchema, RoleFilter
from app.basic.user.services.role_service import RoleService
from core.permissions.permissions import permits

role_router = APIRouter(
    # dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
    responses={"400": {"model": ExceptionResponseSchema}},
)


@role_router.get("", response_model=RoleListSchema)
async def role_list(
        request: Request,
        model_filter: RoleFilter = FilterDepends(RoleFilter),
        size: int = Query(ge=1, le=100, default=100),
):
    data = await RoleService(request).list(model_filter, size)
    cursor = model_filter.lsn__gt
    return {'size': len(data), 'cursor': cursor, 'data': data}


@role_router.get("/permissions_filter", response_model=PermissionListSchema)
async def permission_list_filter(filter: str = Query('', description="filter"), ):
    data = []
    for i, perm in enumerate(permits.items()):
        if filter:
            if not ((filter.lower() in perm[0]) or (filter.lower() in perm[1].lower())):
                continue
        data.append({
            'lsn': i, 'title': perm[0], 'description': perm[1]
        })
    return {'data': data}


@role_router.post("", response_model=RoleScheme)
async def role_create(request: Request, schema: RoleCreateScheme):
    return await RoleService(request).create(obj=schema)


@role_router.get("/{role_id}", response_model=RoleScheme)
async def role_get(request: Request, role_id: uuid.UUID):
    return await RoleService(request).get(id=role_id)


@role_router.put("/{role_id}", response_model=RoleScheme)
async def role_update(request: Request, role_id: uuid.UUID, schema: RoleUpdateScheme):
    return await RoleService(request).update(id=role_id, obj=schema)


@role_router.delete("/{role_id}")
async def role_delete(request: Request, role_id: uuid.UUID):
    await RoleService(request).delete(id=role_id)
