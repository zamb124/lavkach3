from typing import Any, Optional

from app.basic.partner.models import Partner
from app.basic.partner.schemas import PartnerCreateScheme, PartnerUpdateScheme, PartnerFilter
from core.permissions import permit
from core.service.base import BaseService, UpdateSchemaType, ModelType, FilterSchemaType, CreateSchemaType


class PartnerService(BaseService[Partner, PartnerCreateScheme, PartnerUpdateScheme, PartnerFilter]):
    def __init__(self, request=None, db_session=None):
        super(PartnerService, self).__init__(request, Partner, PartnerCreateScheme, PartnerUpdateScheme, db_session)

    @permit('partner_edit')
    async def update(self, id: Any, obj: UpdateSchemaType) -> Optional[ModelType]:
        return await super(PartnerService, self).update(id, obj)

    @permit('partner_list')
    async def list(self, _filter: FilterSchemaType, size: int):
        return await super(PartnerService, self).list(_filter, size)

    @permit('partner_create')
    async def create(self, obj: CreateSchemaType) -> ModelType:
        return await super(PartnerService, self).create(obj)

    @permit('partner_delete')
    async def delete(self, id: Any) -> None:
        return await super(PartnerService, self).delete(id)
