from datetime import datetime
from typing import List, Optional
import uuid
from pydantic import BaseModel, Field, HttpUrl, conint
from pydantic.types import UUID4, condecimal, constr
from app.to_camel import to_camel
from app.store.models.store import Store, StoreType
from core.repository.base import BaseRepo

class StoreBaseScheme(BaseModel, BaseRepo):
    title: str
    external_id: str
    address: Optional[str]
    source: Optional[StoreType]

    class Config:
        model = Store
class StoreUpdateScheme(StoreBaseScheme):
    pass
class StoreCreateScheme(StoreBaseScheme):

    class Config:
        model = Store
class StoreScheme(StoreCreateScheme):
    lsn: int
    id:UUID4
    class Config:
        model = Store
        orm_mode = True
        #alias_generator = to_camel
        #allow_population_by_field_name = True