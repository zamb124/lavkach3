from datetime import datetime
from typing import List, Optional
import uuid
from pydantic import BaseModel, Field, HttpUrl, conint
from pydantic.types import UUID4, condecimal, constr
from app.to_camel import to_camel
from app.maintenance.models import Model
from app.maintenance.schemas.manufacturer import ManufacturerScheme
from core.schemas.timestamps import TimeStampScheme


class ModelBaseScheme(BaseModel):
    title: str = Field(description="Title")
    manufacturer_id: UUID4
class ModelUpdateScheme(ModelBaseScheme):
    pass
class ModelCreateScheme(ModelBaseScheme):
    pass
class ModelScheme(ModelCreateScheme, TimeStampScheme):
    id: UUID4
    lsn: int
    manufacturer: ManufacturerScheme
    class Config:
        orm_mode = True