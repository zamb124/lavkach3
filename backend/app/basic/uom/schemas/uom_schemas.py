from datetime import datetime

from pydantic import BaseModel, Field, UUID4
from typing import Optional, List

from core.schemas.timestamps import TimeStampScheme
from fastapi_filter.contrib.sqlalchemy import Filter
from app.basic.uom.models.uom_models import Uom, UomType
from core.schemas.list_schema import GenericListSchema
from core.schemas import BaseFilter


class UomBaseScheme(BaseModel):
    title: str = Field(title="Title", table=True)
    uom_category_id: UUID4 = Field(title="Uom Categoty", table=True, description='Select category of UOM Category')
    type: UomType = Field(title="Uom Type", table=True, description='Select type \n SMALLER: this category is smaller \n BIGGER... STANDART')
    ratio: float = Field(title="Uom Type", table=True, description='Ratio')
    precision: float = Field(title="Presicion", table=True, description='Precision')

    class Config:
        extra = 'allow'
        from_attributes = True
        orm_model = Uom
        service = 'app.basic.uom.services.UomService'

class UomUpdateScheme(UomBaseScheme):
    ...


class UomCreateScheme(UomBaseScheme):
    ...


class UomScheme(UomCreateScheme, TimeStampScheme):
    company_id: UUID4
    id: UUID4
    lsn: int

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


class UomFilter(BaseFilter):
    title__in: Optional[List[str]] = Field(default=None, description="title")
    uom_category_id__in: Optional[List[str]] = Field(default=None,description="category_id")
    type__in: Optional[List[str]] = Field(default=None, description="type")

    class Config:
        populate_by_name = True

    class Constants(Filter.Constants):
        model = Uom
        ordering_field_name = "order_by"
        search_field_name = "search"
        search_model_fields = ["title", ]


class UomListSchema(GenericListSchema):
    data: Optional[List[UomScheme]]
