from typing import List, Optional

from pydantic import BaseModel
from pydantic.types import UUID4, condecimal

from app.maintenance.models import Order, OrderStatus
from app.store.schemas import StoreScheme
from app.user.schemas import GetUserListResponseSchema
from core.schemas.timestamps import TimeStampScheme


class OrderLineBaseScheme(BaseModel):
    title: str
    description:str
    order_id: UUID4
    quantity: Optional[int]
    cost = condecimal(decimal_places=2)



class OrderLineUpdateScheme(OrderLineBaseScheme):
    pass

class OrderLineCreateScheme(OrderLineBaseScheme):
    pass

class OrderLineScheme(OrderLineCreateScheme, TimeStampScheme):
    id: UUID4
    lsn: int

    class Config:
        orm_mode = True
        # alias_generator = to_camel
        # allow_population_by_field_name = True

##############################################################################################################
class OrderBaseScheme(BaseModel):
    company_id: UUID4
    description: str
    supplier_id: Optional[UUID4]
    status: Optional[OrderStatus]
    asset_id:UUID4
    store_id: UUID4
    user_created_id: UUID4
    supplier_user_id: Optional[UUID4]
    class Config:
        model = Order
class OrderUpdateScheme(OrderBaseScheme):
    pass
class OrderCreateScheme(OrderBaseScheme):
    pass

class OrderCreateByAssetScheme(BaseModel):
    asset_id: UUID4
    description: str
    user_id: UUID4


class OrderScheme(OrderCreateScheme, TimeStampScheme):
    id: UUID4
    lsn: int
    number: int
    store: StoreScheme
    user_created: GetUserListResponseSchema
    supplier_user: Optional[GetUserListResponseSchema]
    order_lines: List[OrderLineScheme]
    class Config:
        orm_mode = True
        #alias_generator = to_camel
        #allow_population_by_field_name = True

class OrderLineInlineScheme(OrderLineCreateScheme):
    id: UUID4
    lsn: int