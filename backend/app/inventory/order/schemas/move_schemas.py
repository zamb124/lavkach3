from datetime import datetime
from typing import Optional, List

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import BaseModel, Field
from pydantic.types import UUID4

from app.inventory.location.enums import LocationClass
from core.schemas import BaseFilter
from core.schemas.list_schema import GenericListSchema
from core.schemas.timestamps import TimeStampScheme
from app.inventory.order.models import Move, MoveType
from app.inventory.order.models.order_models import MoveStatus




class MoveBaseScheme(BaseModel):
    type: MoveType = Field(title='Move Type', table=True)
    order_id: Optional[UUID4] = Field(default=None, title='Order ID', model='order')
    order_type_id: UUID4 = Field(title='Order type', model='order_type')
    store_id: UUID4 = Field(title='Store', table=True, form=True, model='store')
    partner_id: Optional[UUID4] = Field(default=None, title='Partner ID', model='partner')
    location_src_id: Optional[UUID4] = Field(default=None, title='Location src', model='location', table=True, filter={'location_class__not_in': LocationClass.PACKAGE.value})
    location_dest_id: Optional[UUID4] = Field(default=None, title='Location dest', model='location', table=True, filter={'location_class__not_in': LocationClass.PACKAGE.value})
    lot_id: Optional[UUID4] = Field(default=None, title='Lot', table=True, model='lot')
    location_id: Optional[UUID4] = Field(default=None, title='Package', table=True, model='location', filter={'location_class__in': LocationClass.PACKAGE.value})
    # ONE OF Возможно либо location_id либо product_id
    product_id: Optional[UUID4] = Field(default=None, title='Product', table=True, model='product')
    quantity: float = Field(title='Quantity', table=True)
    uom_id: Optional[UUID4] = Field(default=None, title='Uom', table=True, model='uom')
    quant_id: Optional[UUID4] = Field(default=None, title='Quant', table=True, model='quant')

    class Config:
        extra = 'allow'
        from_attributes = True
        orm_model = Move
        service = 'app.inventory.order.services.MoveService'

class MoveUpdateScheme(MoveBaseScheme):
    id: Optional[UUID4] = None


class MoveCreateScheme(MoveBaseScheme):
    ...



class MoveScheme(MoveCreateScheme, TimeStampScheme):
    company_id: UUID4
    lsn: int
    id: UUID4
    move_id: Optional[UUID4] = Field(default=None, model='move', title='Parent Move')
    status: MoveStatus



class MoveFilter(BaseFilter):
    store_id__in: Optional[List[UUID4]] = Field(default=None, title='Store', model='store')

    class Config:
        populate_by_name = True

    class Constants(Filter.Constants):
        model = Move
        ordering_field_name = "order_by"
        search_field_name = "search"
        search_model_fields = ["order_id", "product_id"]


class MoveListSchema(GenericListSchema):
    data: Optional[List[MoveScheme]]

