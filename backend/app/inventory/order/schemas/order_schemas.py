from __future__ import annotations

from datetime import datetime
from typing import Optional, List, Dict

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import computed_field
from pydantic.types import UUID4

from app.inventory.order.enums.order_enum import OrderStatus
from app.inventory.order.models import Order
from app.inventory.order.schemas.move_schemas import MoveScheme, MoveCreateScheme, MoveUpdateScheme
from app.inventory.order.schemas.order_type_schemas import OrderTypeScheme
from core.schemas import BaseFilter
from core.schemas.basic_schemes import BasicField as Field, ActionBaseSchame
from core.schemas.basic_schemes import BasicModel
from core.schemas.list_schema import GenericListSchema
from core.schemas.timestamps import TimeStampScheme
from core.types import UUID


class OrderBaseScheme(BasicModel):
    external_number: Optional[str] = Field(default=None, title='External ID', table=True, form=True)
    order_type_id: UUID = Field(title='Order type', form=True, model='order_type')
    store_id: UUID = Field(title='Store', table=True, form=True, model='store')
    partner_id: Optional[UUID] = Field(default=None, title='Partner', table=True, form=True, model='partner',
                                       readonly=True)
    lot_id: Optional[UUID] = Field(default=None, title='Lot', model='lot')
    origin_type: Optional[str] = Field(default=None, title='Original Type', form=True)
    origin_number: Optional[str] = Field(default=None, title='Original', table=True, form=True)
    planned_datetime: Optional[datetime] = Field(default=None, title='Planned Date', table=True)
    expiration_datetime: Optional[datetime] = Field(default=None, title='Expiration Date', table=False)
    description: Optional[str] = Field(default=None, title='Description', table=False)
    status: OrderStatus = Field(default=OrderStatus.CREATED, title='Status', readonly=True, table=True)
    estatus: Optional[str] = Field(default='done', title='Estatus', table=False)
    order_id: Optional[UUID] = Field(default=None, title='Parent', readonly=True)
    processing_steps: Optional[Dict[str, dict]] = Field(default={}, title='Processing Steps', readonly=True)

    class Config:
        orm_model = Order
        readonly = [('status', '==', 'draft')]  # Переопределяет readonly для всех полей модели для UI


class OrderUpdateScheme(OrderBaseScheme):
    move_list_rel: Optional[list['MoveUpdateScheme']] = Field(default=[], title='Order Movements', model='move')
    order_type_id: Optional[UUID] = Field(
        default=None,
        title='Order type',
        model='order_type',
        readonly=False,
        filter={'status__in': OrderStatus.CREATED.value}
    )


class OrderCreateScheme(OrderBaseScheme):
    move_list_rel: Optional[list[MoveCreateScheme]] = Field(default=[], title='Order Movements', model='move')


class OrderScheme(OrderCreateScheme, TimeStampScheme):
    lsn: int = Field(title='LSN', readonly=True)
    id: UUID4 = Field(title='ID', table=True, readonly=True)
    company_id: UUID = Field(title='Company', model='company')
    vars: Optional[dict] = None
    number: str = Field(title='Order #', readonly=False, description="Internal number of order")
    actual_datetime: Optional[datetime] = Field(title='Actual Date')
    created_by: UUID = Field(title='Created By', model='user')
    edited_by: UUID = Field(title='Edit By', model='user')
    user_ids: Optional[list[UUID]] = Field(default=[], title='Users', readonly=False, model='user', table=True)
    order_type_rel: OrderTypeScheme = Field(title='Order Type', table=True, form=False, readonly=True)
    move_list_rel: Optional[list["MoveScheme"]] = Field(default=[], title='Order Movements', model='move')

    @computed_field(title='Order #', json_schema_extra={'table': False})
    def title(self) -> str:
        "some title"
        return f'{self.number}'


class OrderFilter(BaseFilter):
    planned_datetime__gte: Optional[datetime] = Field(title="bigger or equal planned date", default=None)
    planned_datetime__lt: Optional[datetime] = Field(title="less planned date", default=None)
    status__in: Optional[List[OrderStatus]] = Field(default=None, title='Order Status')
    store_id__in: Optional[List[UUID]] = Field(default=None, title='Store', model='store')
    order_type_id__in: Optional[List[UUID]] = Field(default=None, title='Order Type', model='order_type')

    class Constants(Filter.Constants):
        model = Order
        ordering_field_name = "order_by"
        search_model_fields = ["external_number", "origin_number", "number"]


class OrderListSchema(GenericListSchema):
    data: Optional[List[OrderScheme]]


class OrderConfirm(ActionBaseSchame):
    ...

class OrderComplete(ActionBaseSchame):
    ...
class OrderStart(ActionBaseSchame):
    ...

class AssignUser(ActionBaseSchame):
    user_id: UUID = Field(

        title='User',
        form=True,
        model='user'
    )