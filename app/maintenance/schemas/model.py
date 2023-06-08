from datetime import datetime
from typing import List, Optional
import uuid
from pydantic import BaseModel, Field, HttpUrl, conint
from pydantic.types import UUID4, condecimal, constr
from app.to_camel import to_camel
from app.maintenance.models import Model
from core.repository.base import BaseRepo
from app.maintenance.schemas.manufacturer import ManufacturerScheme

class ModelBaseScheme(BaseModel, BaseRepo):
    title: str = Field(description="Title")
    manufacturer_id: UUID4
    class Config:
        model = Model
class ModelUpdateScheme(ModelBaseScheme):
    pass
class ModelCreateScheme(ModelBaseScheme):

    class Config:
        model = Model
class ModelScheme(ModelCreateScheme):
    id: UUID4
    lsn: int
    manufacturer: ManufacturerScheme
    class Config:
        model = Model
        orm_mode = True
        #alias_generator = to_camel
        #allow_population_by_field_name = True