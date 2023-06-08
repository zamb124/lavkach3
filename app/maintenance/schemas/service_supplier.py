from datetime import datetime
from typing import List, Optional
import uuid
from pydantic import BaseModel, Field, HttpUrl, conint
from pydantic.types import UUID4, condecimal, constr
from app.to_camel import to_camel
from app.maintenance.models import Contractor, ServiceSupplier
from core.repository.base import BaseRepo
from app.maintenance.schemas.contractor import ContractorScheme

class ServiceSupplierBaseScheme(BaseModel, BaseRepo):
    title: str = Field(description="Title")
    external_id: str = Field(description="External ID")
    company_id: UUID4
    contractor_id: UUID4
    class Config:
        model = ServiceSupplier
class ServiceSupplierUpdateScheme(ServiceSupplierBaseScheme):
    pass
class ServiceSupplierCreateScheme(ServiceSupplierBaseScheme):

    class Config:
        model = ServiceSupplier
class ServiceSupplierScheme(ServiceSupplierCreateScheme):
    id: UUID4
    lsn: int
    contractor: ContractorScheme
    class Config:
        model = ServiceSupplier
        orm_mode = True
        #alias_generator = to_camel
        #allow_population_by_field_name = True