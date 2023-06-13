from datetime import datetime
from typing import List, Optional
import uuid
from pydantic import BaseModel, Field, HttpUrl, conint
from pydantic.types import UUID4, condecimal, constr
from app.to_camel import to_camel
from app.maintenance.models import ServiceSupplier, Manufacturer
from app.maintenance.schemas.contractor import ContractorScheme
from core.schemas.timestamps import TimeStampScheme
class ManufacturerBaseScheme(BaseModel):
    title: str = Field(description="Title")
    company_id: UUID4

class ManufacturerUpdateScheme(ManufacturerBaseScheme):
    pass
class ManufacturerCreateScheme(ManufacturerBaseScheme):
    pass

class ManufacturerScheme(ManufacturerCreateScheme, TimeStampScheme):
    id: UUID4
    lsn: int
    class Config:
        orm_mode = True
