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
from app.inventory.order.models.order_models import MoveStatus, ReservationMethod



class MoveBaseScheme(BaseModel):
    type: MoveType = Field(title='Move Type')
    location_src_id: Optional[UUID4] = Field(default=None, title='Location src', table=True, )
    location_dest_id: Optional[UUID4] = Field(default=None, title='Location dest', table=True)
    lot_id: Optional[UUID4] = Field(default=None, title='Lot', table=True)
    location_id: Optional[UUID4] = Field(default=None, title='Package', table=True, filter={'location_class__in': LocationClass.PACKAGE})
    # ONE OF Возможно либо location_id либо product_id
    product_id: Optional[UUID4] = Field(default=None, title='Product', table=True)
    quantity: float = Field(title='Quantity', table=True)
    uom_id: Optional[UUID4] = Field(default=None, title='Uom', table=True)

    class Config:
        extra = 'allow'
        from_attributes = True
        orm_model = Move
        service = 'app.inventory.order.services.MoveService'

class MoveUpdateScheme(MoveBaseScheme):
    id: Optional[UUID4] = None


class MoveCreateScheme(MoveBaseScheme):
    order_id: UUID4



class MoveScheme(MoveCreateScheme, TimeStampScheme):
    company_id: UUID4
    lsn: int
    id: UUID4
    move_id: Optional[UUID4] = None
    partner_id: Optional[UUID4] = None
    status: MoveStatus

    class Config:
        from_attributes = True


class MoveFilter(BaseFilter):
    store_id__in: Optional[List[UUID4]] = Field(default=None, title='Store')

    class Config:
        populate_by_name = True

    class Constants(Filter.Constants):
        model = Move
        ordering_field_name = "order_by"
        search_field_name = "search"
        search_model_fields = ["order_id", "product_id"]


class MoveListSchema(GenericListSchema):
    data: Optional[List[MoveScheme]]

