import datetime
import uuid
from typing import Any, Optional, List

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.exceptions import HTTPException

from app.inventory.order.enums.exceptions_suggest_enums import SuggestErrors
from app.inventory.order.enums.order_enum import SuggestStatus, SuggestType
from app.inventory.order.models.order_models import Suggest
from app.inventory.order.schemas.suggest_schemas import SuggestCreateScheme, SuggestUpdateScheme, SuggestFilter
from core.exceptions.module import ModuleException
from core.permissions import permit
from core.service.base import BaseService, UpdateSchemaType, ModelType, FilterSchemaType, CreateSchemaType


class SuggestService(BaseService[Suggest, SuggestCreateScheme, SuggestUpdateScheme, SuggestFilter]):
    def __init__(self, request, db_session: AsyncSession = None):
        super(SuggestService, self).__init__(request, Suggest, SuggestCreateScheme, SuggestUpdateScheme, db_session)

    @permit('suggest_edit')
    async def update(self, id: Any, obj: UpdateSchemaType, commit=False) -> Optional[ModelType]:
        return await super(SuggestService, self).update(id, obj, commit=commit)

    @permit('suggest_list')
    async def list(self, _filter: FilterSchemaType | dict, size: int):
        return await super(SuggestService, self).list(_filter, size)

    @permit('suggest_create')
    async def create(self, obj: CreateSchemaType, commit=False) -> ModelType:
        return await super(SuggestService, self).create(obj, commit)

    @permit('suggest_delete')
    async def delete(self, id: Any) -> None:
        return await super(SuggestService, self).delete(id)

    @permit('suggest_confirm')
    async def suggest_confirm(self, suggest_ids: List[uuid.UUID], value, commit=True) -> Optional[ModelType]:
        suggest_entities = await self.list({'id__in': suggest_ids}, 999)
        try:
            value = float(value)
        except ValueError as e:
            raise ModuleException(
                status_code=406,
                enum=SuggestErrors.SUGGEST_INVALID_VALUE,
                message=str(e)
            )
        for suggest_entity in suggest_entities:
            if suggest_entity.status == SuggestStatus.DONE:
                raise ModuleException(
                    status_code=406,
                    enum=SuggestErrors.SUGGEST_ALREADY_DONE
                )
            elif suggest_entity.type == SuggestType.IN_QUANTITY:
                val_in_cleaned = float(value)
                val_s_cleaned = float(suggest_entity.value)
                if val_in_cleaned == val_s_cleaned:
                    suggest_entity.status = SuggestStatus.DONE
            elif suggest_entity.type == SuggestType.IN_PRODUCT:
                product_obj = await self.env['product'].adapter.product_by_barcode(value)
                if product_obj:
                    suggest_entity.status = SuggestStatus.DONE
            elif suggest_entity.type == SuggestType.IN_LOCATION:
                location_entity = await self.env['location'].service.list(_filter={'id__in': [value]})
                if location_entity:
                    suggest_entity.status = SuggestStatus.DONE
            else:
                raise ModuleException(
                    status_code=500,
                    enum=SuggestErrors.SUGGEST_TYPE_NOT_FOUND,
                )
            suggest_entity.user_id = self.user.user_id
        if commit:
            try:
                await self.session.commit()
                [await self.session.refresh(i) for i in suggest_entities]
            except Exception as e:
                await self.session.rollback()
                raise HTTPException(status_code=500, detail=f"Some Error entity {str(e)}")
        else:
            await self.session.flush(suggest_entities)
        return suggest_entities
