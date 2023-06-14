from typing import Optional, Any

from pydantic import BaseModel, Json
from pydantic.types import UUID4
from app.store.models.store import StoreType
from core.schemas.timestamps import TimeStampScheme


class StoreBaseScheme(BaseModel):
    company_id: UUID4
    vars: Optional[dict]
    title: str
    external_id: str
    address: Optional[str]
    source: Optional[StoreType]


class StoreUpdateScheme(StoreBaseScheme):
    pass


class StoreCreateScheme(StoreBaseScheme):
    pass


class StoreScheme(StoreCreateScheme, TimeStampScheme):
    lsn: int
    id: UUID4

    class Config:
        orm_mode = True
