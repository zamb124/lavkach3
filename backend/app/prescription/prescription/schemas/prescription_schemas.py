from typing import Optional, List

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import Field
from pydantic.types import UUID

from app.prescription.prescription.models.prescription_models import IdentificationType
from app.prescription.prescription.models.prescription_models import Prescription
from core.schemas import BaseFilter
from core.schemas.basic_schemes import BasicModel
from core.schemas.list_schema import GenericListSchema
from core.schemas.timestamps import TimeStampScheme


class PrescriptionBaseScheme(BasicModel):
    vars: Optional[dict] = None
    title: str = Field(title='Title', table=True, form=True)
    external_number: Optional[str] = Field(default=None, title='External ID', table=True, form=True)
    address: Optional[str] = Field(title='Address', table=True, form=True)
    source: Optional[IdentificationType] = Field(default=IdentificationType.PASSPORT, title='Source',
                                               table=True, form=True)

    class Config:
        orm_model = Prescription


class PrescriptionUpdateScheme(PrescriptionBaseScheme):
    title: str = Field(title='Title', table=True, form=True)
    source: Optional[IdentificationType] = Field(default=None, title='Source', table=True, form=True)


class PrescriptionCreateScheme(PrescriptionBaseScheme):
    pass


class PrescriptionScheme(PrescriptionCreateScheme, TimeStampScheme):
    company_id: UUID = Field(title='Company ID', model='company')
    lsn: int
    id: UUID


class PrescriptionFilter(BaseFilter):
    title__ilike: Optional[str] = Field(default=None, title='Title')
    address__ilike: Optional[str] = Field(description="address", default=None, title='Address')
    source__in: Optional[list[IdentificationType]] = Field(default=None, title='Source')

    class Config:
        populate_by_name = True

    class Constants(Filter.Constants):
        model = Prescription
        ordering_field_name = "order_by"
        search_field_name = "search"
        search_model_fields = ["title", "external_number", "address"]


class PrescriptionListSchema(GenericListSchema):
    data: Optional[List[PrescriptionScheme]]
