from datetime import datetime

from pydantic import BaseModel, Field, UUID4
from typing import Optional, List

from core.schemas.timestamps import TimeStampScheme
from fastapi_filter.contrib.sqlalchemy import Filter
from app.basic.uom.models.uom_models import Uom, UomType
from core.schemas.list_schema import GenericListSchema
from core.helpers.fastapi_filter_patch import BaseFilter


class UomBaseScheme(BaseModel):
    title: str = Field(description="Title")
    external_id: Optional[str]
    category_id: UUID4
    company_id: UUID4
    type: UomType
    ratio: float
    precision: float


class UomUpdateScheme(UomBaseScheme):
    pass


class UomCreateScheme(UomBaseScheme):
    pass


class UomScheme(UomCreateScheme, TimeStampScheme):
    id: UUID4
    lsn: int

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


class UomFilter(BaseFilter):
    lsn__gt: Optional[int] = Field(alias="cursor")
    id__in: Optional[List[UUID4]] = Field(alias="id")
    created_at_gte: Optional[datetime] = Field(description="bigger or equal created")
    created_at_lt: Optional[datetime] = Field(description="less created")
    updated_at_gte: Optional[datetime] = Field(description="bigger or equal updated")
    updated_at_lt: Optional[datetime] = Field(description="less updated")
    title__in: Optional[List[str]] = Field(description="title")
    category_id__in: Optional[List[str]] = Field(description="category_id")
    type__in: Optional[List[str]] = Field(description="type")

    class Config:
        populate_by_name = True

    class Constants(Filter.Constants):
        model = Uom
        ordering_field_name = "order_by"
        search_field_name = "search"
        search_model_fields = ["title", ]


class UomListSchema(GenericListSchema):
    data: Optional[List[UomScheme]]
