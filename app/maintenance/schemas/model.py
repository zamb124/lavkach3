from pydantic import BaseModel, Field
from pydantic.types import UUID4

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