from datetime import datetime
from typing import List, Optional
import uuid
from pydantic import BaseModel, Field, HttpUrl, conint
from pydantic.types import UUID4, condecimal, constr
from app.to_camel import to_camel
from app.maintenance.models import Contractor, ServiceSupplier
from app.maintenance.schemas.contractor import ContractorScheme
from core.schemas.timestamps import TimeStampScheme

class ServiceSupplierBaseScheme(BaseModel):
    title: str = Field(description="Title")
    external_id: str = Field(description="External ID")
    contractor_id: UUID4
class ServiceSupplierUpdateScheme(ServiceSupplierBaseScheme):
    pass
class ServiceSupplierCreateScheme(ServiceSupplierBaseScheme):
    pass
class ServiceSupplierScheme(ServiceSupplierCreateScheme, TimeStampScheme):
    id: UUID4
    lsn: int
    contractor: ContractorScheme
    class Config:
        orm_mode = True