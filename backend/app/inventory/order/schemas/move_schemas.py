from __future__ import annotations

from typing import Optional, List, Dict

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import computed_field
from pydantic.types import UUID4

from app.inventory.location.enums import LocationClass
from app.inventory.order.enums.order_enum import MoveStatus, MoveType
from app.inventory.order.models import Move
from app.inventory.order.schemas.suggest_schemas import SuggestScheme, SuggestCreateScheme, SuggestUpdateScheme
from core.schemas import BaseFilter
from core.schemas.basic_schemes import ActionBaseSchame, BasicModel
from core.schemas.basic_schemes import BasicField as Field
from core.schemas.list_schema import GenericListSchema
from core.schemas.timestamps import TimeStampScheme


class MoveBaseScheme(BasicModel):
    type: MoveType = Field(title='Move Type', table=True, readonly=True)
    order_id: Optional[UUID4] = Field(default=None, title='Order ID', model='order')
    order_type_id: UUID4 = Field(title='Order type', model='order_type', table=True)
    store_id: UUID4 = Field(title='Store', table=True, form=True, model='store')

    partner_id: Optional[UUID4] = Field(default=None, title='Partner ID', model='partner')
    location_src_id: Optional[UUID4] = Field(default=None, title='Location src', model='location', table=True, filter={'location_class__not_in': LocationClass.PACKAGE.value})
    location_dest_id: Optional[UUID4] = Field(default=None, title='Location dest', model='location', table=True, filter={'location_class__not_in': LocationClass.PACKAGE.value})
    lot_id: Optional[UUID4] = Field(default=None, title='Lot', table=True, model='lot')
    package_id: Optional[UUID4] = Field(default=None, title='Package', table=True, model='location', filter={'location_class__in': LocationClass.PACKAGE.value})
    # ONE OF Возможно либо location_id либо product_id
    product_id: Optional[UUID4] = Field(default=None, title='Product', table=True, model='product')
    quantity: float = Field(title='Quantity', table=True)
    uom_id: Optional[UUID4] = Field(default=None, title='Uom', table=True, model='uom')
    quant_src_id: Optional[UUID4] = Field(default=None, title='Quant source', table=True, model='quant')
    quant_dest_id: Optional[UUID4] = Field(default=None, title='Quant dest', table=True, model='quant')
    status: Optional[MoveStatus] = Field(default=MoveStatus.CREATED, title='Status', table=True, readonly=True)
    processing_steps: Optional[Dict[str, dict]] = Field(default={},title='Processing Steps', readonly=True)

    class Config:
        orm_model = Move


class MoveUpdateScheme(MoveBaseScheme):
    suggest_list_rel: Optional[list[SuggestUpdateScheme]] = Field(default=[], title='Suggests', form=True)
    order_id: Optional[UUID4] = Field(default=None, title='Order ID', model='order',readonly=True)
    ...


class MoveCreateScheme(MoveBaseScheme):
    suggest_list_rel: Optional[list[SuggestCreateScheme]] = Field(default=[], title='Suggests', form=True)
    ...


class MoveScheme(MoveCreateScheme, TimeStampScheme):
    company_id: UUID4 = Field(model='company', title='Company')
    lsn: int
    id: UUID4
    created_by: UUID4 = Field(title='Created By',  model='user')
    edited_by: UUID4 = Field(title='Edit By', model='user')
    move_id: Optional[UUID4] = Field(default=None, model='move', title='Parent Move')
    suggest_list_rel: Optional[list[SuggestScheme]] = Field(default=[], title='Suggests', form=True)

    @computed_field
    def title(self) -> str:
        return f'[{self.type.name}] - {self.quantity} - {self.status.name}'

    @computed_field(title='Suggests', json_schema_extra={'table': True})
    def suggest_list_count(self) -> str:
        return f'{len(self.suggest_list_rel)}'


class MoveFilter(BaseFilter):
    store_id__in: Optional[List[UUID4]] = Field(default=None, title='Store', model='store')
    order_id__in: Optional[List[UUID4]] = Field(default=None, title='Order', model='order')

    class Config:
        populate_by_name = True

    class Constants(Filter.Constants):
        model = Move
        ordering_field_name = "order_by"
        search_field_name = "search"
        search_model_fields = ["order_id", "product_id"]


class MoveListSchema(GenericListSchema):
    data: Optional[List[MoveScheme]]

class MoveConfirmScheme(ActionBaseSchame):

    class Config:
        extra = 'allow'

class GetMovesByBarcode(BasicModel):
    barcode: str
    order_id: Optional[UUID4]