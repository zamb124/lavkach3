from datetime import datetime
from typing import Optional, List

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import BaseModel, Field
from pydantic.types import UUID4

from app.inventory.location.enums import PutawayStrategy
from core.schemas import BaseFilter
from core.schemas.list_schema import GenericListSchema
from core.schemas.timestamps import TimeStampScheme
from app.inventory.order.models import Move, MoveType
from app.inventory.order.models.order_models import MoveStatus, ReservationMethod


class MoveBaseScheme(BaseModel):
    type: MoveType
    move_id: Optional[UUID4] = None
    order_id: UUID4
    location_src_id: Optional[UUID4] = None
    location_dest_id: Optional[UUID4] = None
    lot_id: Optional[UUID4] = None
    location_id: Optional[UUID4] = None
    # ONE OF Возможно либо location_id либо product_id
    product_id: Optional[UUID4] = None
    partner_id: Optional[UUID4] = None
    quantity: float
    uom_id: Optional[UUID4] = None

class MoveUpdateScheme(MoveBaseScheme):
    quantity: Optional[float] = None


class MoveCreateScheme(MoveBaseScheme):
    company_id: UUID4



class MoveScheme(MoveCreateScheme, TimeStampScheme):
    lsn: int
    id: UUID4
    type: MoveType
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

