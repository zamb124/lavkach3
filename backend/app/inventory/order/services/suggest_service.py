import logging
import traceback
import uuid
from typing import Any, Optional, List
from zoneinfo import available_timezones

from fastapi.exceptions import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from app.inventory.order.enums.exceptions_suggest_enums import SuggestErrors
from app.inventory.order.enums.order_enum import SuggestStatus, SuggestType, MoveStatus
from app.inventory.order.models.order_models import Suggest
from app.inventory.order.schemas.suggest_schemas import SuggestCreateScheme, SuggestUpdateScheme, SuggestFilter
from core.exceptions.module import ModuleException
from core.permissions import permit
from core.service.base import BaseService, UpdateSchemaType, ModelType, FilterSchemaType, CreateSchemaType
from core.helpers.broker.tkq import list_brocker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SuggestService(BaseService[Suggest, SuggestCreateScheme, SuggestUpdateScheme, SuggestFilter]):
    def __init__(self, request: Request):
        super(SuggestService, self).__init__(request, Suggest, SuggestCreateScheme, SuggestUpdateScheme)

    @permit('suggest_update')
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
    async def suggest_confirm(self, suggest_id: List[uuid.UUID], value: Any, commit: bool = True) -> Optional[ModelType]:
        suggest_entity = await self.get(suggest_id)
        move_service = self.env['move'].service
        move = await move_service.get(suggest_entity.move_id)
        is_last = True
        move_id = suggest_entity.move_id
        if suggest_entity.status == SuggestStatus.DONE:
            raise ModuleException(
                status_code=406,
                enum=SuggestErrors.SUGGEST_ALREADY_DONE
            )
        elif suggest_entity.type == SuggestType.IN_QUANTITY:
            try:
                val_in_cleaned = float(value)
            except ValueError as e:
                raise ModuleException(
                    status_code=406,
                    enum=SuggestErrors.SUGGEST_INVALID_VALUE,
                    message=str(e)
                )
            #TODO: Здесь нужно вставить проверки на overdelivery, ZERO CONDITION и т.д.
            suggest_entity.result_value = str(val_in_cleaned) # Перекладываем в str тк поле универсальное str
            suggest_entity.status = SuggestStatus.DONE
        elif suggest_entity.type == SuggestType.IN_PRODUCT:
            product_obj = await self.env['product'].adapter.product_by_barcode(value)
            if product_obj:
                suggest_entity.result_value = value
                suggest_entity.status = SuggestStatus.DONE
        elif suggest_entity.type == SuggestType.IN_LOCATION_SRC:
            try:
                val_in_cleaned = uuid.UUID(value)  # type: ignore
            except ValueError as e:
                raise ModuleException(
                    status_code=406,
                    enum=SuggestErrors.SUGGEST_INVALID_VALUE,
                    message=str(e)
                )
            location_entity = await self.env['location'].service.get(val_in_cleaned)
            if location_entity:
                #TODO: Здесь нужно вставить проверки на проверку подходящего места назначения
                suggest_entity.result_value = value
                suggest_entity.status = SuggestStatus.DONE
        elif suggest_entity.type == SuggestType.IN_LOCATION_DEST:
            try:
                val_in_cleaned = uuid.UUID(value)  # type: ignore
            except ValueError as e:
                raise ModuleException(
                    status_code=406,
                    enum=SuggestErrors.SUGGEST_INVALID_VALUE,
                    message=str(e)
                )
            location_entity = await self.env['location'].service.get(val_in_cleaned)
            if location_entity:
                if move.location_dest_id != location_entity.id:
                    await move_service.change_dest_location(move, location_entity)
                suggest_entity.result_value = value
                suggest_entity.status = SuggestStatus.DONE
        else:
            raise ModuleException(
                status_code=500,
                enum=SuggestErrors.SUGGEST_TYPE_NOT_FOUND,
            )
        suggest_entity.user_id = self.user.user_id
    # КОСТЫЛЬ: Проверяем не последний ли это саджест, если последний окаем Мув

        for suggest in move.suggest_list_rel:
            if suggest.id != suggest_entity.id and suggest.status != SuggestStatus.DONE:
                is_last = False
        if commit:
            try:
                if is_last:
                    move.status = MoveStatus.COMPLETING
                await self.session.commit()
                if is_last:
                    await self.env['move'].service.set_done.kiq(None, move_id=move_id, user_id=self.user.user_id)
                await self.session.refresh(suggest_entity)
                await suggest_entity.notify('update')
            except Exception as e:
                await self.session.rollback()
                logging.error("Произошла ошибка: %s", e)
                logging.error("Трейсбек ошибки:\n%s", traceback.format_exc())
                raise e

        return suggest_entity
