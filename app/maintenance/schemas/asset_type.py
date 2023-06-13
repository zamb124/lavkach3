from datetime import datetime
from typing import List, Optional
import uuid
from pydantic import BaseModel, Field, HttpUrl, conint
from pydantic.types import UUID4, condecimal, constr
from app.to_camel import to_camel
from app.maintenance.models import AssetType, Type, SourceType
from core.schemas.timestamps import TimeStampScheme
class AssetTypeBaseScheme(BaseModel):
    title: str = Field(description="Title")
    company_id: UUID4
    type: Type
    source: SourceType
    serial_required: Optional[bool]

class AssetTypeUpdateScheme(AssetTypeBaseScheme):
    pass
class AssetTypeCreateScheme(AssetTypeBaseScheme):
    pass
class AssetTypeScheme(AssetTypeCreateScheme, TimeStampScheme):
    id: UUID4
    lsn: int
    class Config:
        orm_mode = True
        #alias_generator = to_camel
        #allow_population_by_field_name = True