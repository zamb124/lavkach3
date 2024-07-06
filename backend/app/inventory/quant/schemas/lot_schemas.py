from datetime import datetime
from typing import Optional, List

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic.types import UUID4

from app.inventory.quant.models import Lot
from core.schemas import BaseFilter
from core.schemas.basic_schemes import BasicModel
from core.schemas.list_schema import GenericListSchema
from core.schemas.timestamps import TimeStampScheme


class LotBaseScheme(BasicModel):
    vars: Optional[dict] = None
    expiration_datetime: Optional[datetime] = None
    product_id: UUID4
    external_number: Optional[str] = None
    partner_id: Optional[UUID4] = None

    class Config:
        extra = 'allow'
        from_attributes = True
        orm_model = Lot
        service = 'app.inventory.quant.services.LotService'



class LotUpdateScheme(LotBaseScheme):
    pass


class LotCreateScheme(LotBaseScheme):
    company_id: UUID4


class LotScheme(LotCreateScheme, TimeStampScheme):
    lsn: int
    id: UUID4

    class Config:
        from_attributes = True


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
