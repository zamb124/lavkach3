import uuid

from fastapi import APIRouter, Query
from starlette.requests import Request

from app.basic.user.schemas import (
    RoleScheme,
    RoleCreateScheme,
    RoleUpdateScheme,
    ExceptionResponseSchema,
    PermissionListSchema,
    PermissionSchema
)
from app.basic.user.services.role_service import RoleService
from core.permissions.permissions import permits

role_router = APIRouter(
    # dependencies=[Depends(PermissionDependency([IsAuthenticated]))],
    responses={"400": {"model": ExceptionResponseSchema}},
)


@role_router.get("/permissions_filter", response_model=PermissionListSchema)
async def permission_list_filter(filter: str = Query('', description="filter"), ):
    perms = []
    for i, perm in enumerate(permits.items()):
        if filter:
            if not ((filter.lower() in perm[0]) or (filter.lower() in perm[1].lower())):
                continue
        perms.append(PermissionSchema(**{
            'lsn': i, 'title': perm[0], 'description': perm[1]
        }))
    return perms


@role_router.post("/create", response_model=RoleScheme)
async def role_create(request: Request, schema: RoleCreateScheme):
    return await RoleService(request).create(obj=schema)


@role_router.get("/{role_id}")
async def role_get(request: Request, role_id: uuid.UUID):
    return await RoleService(request).get(id=role_id)


@role_router.put("/{role_id}", response_model=RoleScheme)
async def role_update(request: Request, role_id: uuid.UUID, schema: RoleUpdateScheme):
    return await RoleService(request).update(id=role_id, obj=schema)


@role_router.delete("/{role_id}")
async def role_delete(request: Request, role_id: uuid.UUID):
    await RoleService(request).delete(id=role_id)
