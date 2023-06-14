from pydantic import BaseModel, Field
from pydantic.types import UUID4

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
