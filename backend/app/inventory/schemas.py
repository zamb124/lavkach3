from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.inventory.location.enums import LocationClass, PhysicalStoreLocationClass
from app.inventory.order import MoveCreateScheme, OrderTypeScheme
from app.inventory.quant import QuantScheme
from core.schemas.basic_schemes import BasicField as Field


class Quant(QuantScheme):
    order_types: Optional[list[OrderTypeScheme]] = Field(default=[], title='Order Types', form=True, model='order_type')
    qty_to_move: Optional[float] = Field(default=0.0, title='Quantity to move', form=True)
    location_dest_id: Optional[UUID] = Field(default=None, title='Destination Location', form=True, model='location')


class Product(BaseModel):
    product_id: UUID = Field(title='Product', form=True, model='product')
    quantity: float = Field(title='Quantity', form=True)
    avaliable_quantity: float = Field(default=0.0, title='Avaliable Quantity', form=True)
    lot_id: Optional[UUID] = Field(default=None, title='Lot', form=True, model='lot')
    uom_id: Optional[UUID] = Field(default=None, title='UOM', form=True, model='uom')
    quants: Optional[list[Quant]] = Field(default=[], title='Quants', form=True)
    moves: Optional[list[MoveCreateScheme]] = Field(default=[], title='Moves', form=True, model='move')


class Package(BaseModel):
    package_id: UUID = Field(title='Package', form=True, model='location',
                             filter={'location_class__in': LocationClass.PACKAGE.value})
    quants: Optional[list[Quant]] = Field(default=[], title='Quants', form=True)
    moves: Optional[list[MoveCreateScheme]] = Field(default=[], title='Moves', form=True, model='move')


class CreateMovements(BaseModel):
    external_number: Optional[str] = Field(default=None, title='External ID', form=True)
    order_type_id: Optional[UUID] = Field(default=None, title='Order type', form=True, model='order_type')
    store_id: UUID = Field(title='Store', table=True, form=True, model='store')
    location_src_id: Optional[UUID] = Field(default=None, title='Source Location', form=True, model='location')
    location_dest_id: Optional[UUID] = Field(default=None, title='Source Location', form=True, model='location')
    location_src_zone_id: Optional[UUID] = Field(default=None, title='Source Zone', form=True, model='location')
    location_dest_zone_id: Optional[UUID] = Field(default=None, title='Destination Zone', form=True, model='location')
    location_type_src_id: Optional[UUID] = Field(default=None, title='Source Location Type', form=True,
                                                 model='location_type')
    location_type_dest_id: Optional[UUID] = Field(default=None, title='Destination Location Type', form=True,
                                                  model='location_type')
    location_class_src_id: Optional[PhysicalStoreLocationClass] = Field(
        default=None, title='Source Location Class', form=True
    )
    location_class_dest_id: Optional[PhysicalStoreLocationClass] = Field(
        default=None, title='Destination Location Class', form=True
    )
    partner_id: Optional[UUID] = Field(default=None, title='Partner', form=True, model='partner')
    origin_number: Optional[str] = Field(default=None, title='Original', form=True)
    planned_datetime: Optional[datetime] = Field(default=None, title='Planned Date', form=True)
    expiration_datetime: Optional[datetime] = Field(default=None, title='Expiration Date', form=False)
    description: Optional[str] = Field(default=None, title='Description', form=True)
    products: list[Product] = Field(default=[], title='Products', form=True)
    packages: list[Package] = Field(default=[], title='Packages', form=True)
