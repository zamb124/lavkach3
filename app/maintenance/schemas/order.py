from datetime import datetime
from typing import List, Optional
import uuid
from pydantic import BaseModel, Field, HttpUrl
from pydantic.types import UUID4, condecimal, constr, condecimal
from app.maintenance.models import Order, OrderLine, OrderStatus
from core.repository.base import BaseRepo
from app.store.schemas import StoreScheme
from app.user.schemas import GetUserListResponseSchema
from pydantic import ConfigDict

class OrderLineBaseScheme(BaseModel, BaseRepo):
    title: str
    description:str
    order_id: UUID4
    quantity: Optional[int]
    cost = condecimal(decimal_places=2)

    class Config:
        model = OrderLine

class OrderLineUpdateScheme(OrderLineBaseScheme):
    pass

class OrderLineCreateScheme(OrderLineBaseScheme):
    class Config:
        model = OrderLine

class OrderLineScheme(OrderLineCreateScheme):
    id: UUID4
    lsn: int

    class Config:
        model = OrderLine
        orm_mode = True
        # alias_generator = to_camel
        # allow_population_by_field_name = True

##############################################################################################################
class OrderBaseScheme(BaseModel, BaseRepo):
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
    class Config:
        model = Order

class OrderCreateByAssetScheme(BaseModel, BaseRepo):
    asset_id: UUID4
    description: str
    user_id: UUID4
    class Config:
        model = Order
        orm_mode = True


class OrderScheme(OrderCreateScheme):
    id: UUID4
    lsn: int
    number: int
    store: StoreScheme
    user_created: GetUserListResponseSchema
    supplier_user: Optional[GetUserListResponseSchema]
    order_lines: List[OrderLineScheme]
    class Config:
        model = Order
        orm_mode = True
        #alias_generator = to_camel
        #allow_population_by_field_name = True

class OrderLineInlineScheme(OrderLineCreateScheme):
    id: UUID4
    lsn: int