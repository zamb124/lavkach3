from datetime import datetime
from typing import List, Optional
import uuid
from pydantic import BaseModel, Field, HttpUrl, conint
from pydantic.types import UUID4, condecimal, constr
from app.to_camel import to_camel
from app.maintenance.models import ServiceSupplier, Manufacturer
from core.repository.base import BaseRepo
from app.maintenance.schemas.contractor import ContractorScheme

class ManufacturerBaseScheme(BaseModel, BaseRepo):
    title: str = Field(description="Title")
    company_id: UUID4
    class Config:
        model = Manufacturer
class ManufacturerUpdateScheme(ManufacturerBaseScheme):
    pass
class ManufacturerCreateScheme(ManufacturerBaseScheme):

    class Config:
        model = Manufacturer
class ManufacturerScheme(ManufacturerCreateScheme):
    id: UUID4
    lsn: int
    class Config:
        model = Manufacturer
        orm_mode = True
        #alias_generator = to_camel
        #allow_population_by_field_name = True