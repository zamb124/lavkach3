from typing import Optional

from pydantic import BaseModel
from pydantic.types import UUID4
from app.basic.store.models.store_models import StoreType
from core.schemas.timestamps import TimeStampScheme
from app.basic.company.schemas import CompanyScheme


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
    company: CompanyScheme

    class Config:
        orm_mode = True
