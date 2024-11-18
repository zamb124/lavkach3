import logging
import uuid
from typing import Any

from starlette.requests import Request

from app.inventory.order.models.order_models import MoveLog, Order
from app.inventory.order.schemas.move_log_schemas import MoveLogCreateScheme, MoveLogUpdateScheme, MoveLogFilter
# from app.inventory.order.services.move_log_tkq import move_log_set_done
from core.permissions import permit
from core.service.base import BaseService, UpdateSchemaType, ModelType, FilterSchemaType, CreateSchemaType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MoveLogService(BaseService[MoveLog, MoveLogCreateScheme, MoveLogUpdateScheme, MoveLogFilter]):
    def __init__(self, request: Request):
        super(MoveLogService, self).__init__(request, MoveLog, MoveLogCreateScheme, MoveLogUpdateScheme)

    @permit('move_log_update')
    async def update(self, id: Any, obj: UpdateSchemaType, commit: bool = True):
        return await super(MoveLogService, self).update(id, obj, commit)

    @permit('move_log_list')
    async def list(self, _filter: FilterSchemaType, size: int=100):
        return await super(MoveLogService, self).list(_filter, size)

    @permit('move_log_create')
    async def create(self, obj: CreateSchemaType, parent: Order | MoveLog | None = None, commit=True) -> ModelType:
        if isinstance(obj, dict):
            obj = self.create_schema(**obj)
        obj.created_by = self.user.user_id
        obj.edited_by = self.user.user_id
        return await super(MoveLogService, self).create(obj)

    @permit('move_log_delete')
    async def delete(self, id: uuid.UUID) -> bool:
        return await super(MoveLogService, self).delete(id)
