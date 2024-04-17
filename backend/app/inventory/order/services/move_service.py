import datetime
import uuid
from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.inventory.order.models.order_models import Move, MoveType
from app.inventory.order.schemas.move_schemas import MoveCreateScheme, MoveUpdateScheme, MoveFilter
from core.db.session import session
from core.permissions import permit
from core.service.base import BaseService, UpdateSchemaType, ModelType, FilterSchemaType, CreateSchemaType



class MoveService(BaseService[Move, MoveCreateScheme, MoveUpdateScheme, MoveFilter]):
    def __init__(self, request, db_session: AsyncSession = None):
        super(MoveService, self).__init__(request, Move, MoveCreateScheme, MoveUpdateScheme, db_session)

    @permit('move_edit')
    async def update(self, id: Any, obj: UpdateSchemaType, commit:bool =True) -> Optional[ModelType]:
        return await super(MoveService, self).update(id, obj, commit)

    @permit('move_list')
    async def list(self, _filter: FilterSchemaType, size: int):
        return await super(MoveService, self).list(_filter, size)

    @permit('move_create')
    async def create(self, obj: CreateSchemaType, commit=True) -> ModelType:
        return await super(MoveService, self).create(obj, commit)

    @permit('move_delete')
    async def delete(self, id: Any) -> None:
        return await super(MoveService, self).delete(id)


    @permit('move_move_counstructor')
    async def move_counstructor(self, move_id: uuid.UUID, moves: list) -> None:
        return await super(MoveService, self).delete(id)
