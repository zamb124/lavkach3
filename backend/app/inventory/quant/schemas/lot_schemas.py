from datetime import datetime
from typing import Optional, List

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import BaseModel, Field
from pydantic.types import UUID4

from core.schemas import BaseFilter
from core.schemas.list_schema import GenericListSchema
from core.schemas.timestamps import TimeStampScheme
from app.inventory.quant.models import Lot


class LotBaseScheme(BaseModel):
    vars: Optional[dict] = None
    expiration_datetime: Optional[datetime] = None
    product_id: UUID4
    external_number: Optional[str] = None
    partner_id: Optional[UUID4] = None


class LotUpdateScheme(LotBaseScheme):
    pass


class LotCreateScheme(LotBaseScheme):
    company_id: UUID4


class LotScheme(LotCreateScheme, TimeStampScheme):
    lsn: int
    id: UUID4

    class Config:
        orm_mode = True


class LotFilter(BaseFilter):
    class Config:
        populate_by_name = True

    class Constants(Filter.Constants):
        model = Lot
        ordering_field_name = "order_by"
        search_field_name = "search"
        search_model_fields = ["external_number"]


class LotListSchema(GenericListSchema):
    data: Optional[List[LotScheme]]
