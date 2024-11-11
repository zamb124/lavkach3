from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.inventory.location.enums import LocationClass
from core.schemas.basic_schemes import BasicField as Field


class Product(BaseModel):
    product_id: UUID = Field(title='Product', form=True, model='product')
    quantity: float = Field(title='Quantity', form=True)
    lot_id: Optional[UUID] = Field(default=None, title='Lot', form=True, model='lot')
    uom_id: Optional[UUID] = Field(default=None, title='UOM', form=True, model='uom')


class Package(BaseModel):
    package_id: Optional[UUID] = Field(default=None, title='Package', form=True, model='location',
                                       filter={'location_class__in': LocationClass.PACKAGE.value})


class CreateMovements(BaseModel):
    external_number: Optional[str] = Field(default=None, title='External ID', form=True)
    order_type_id: UUID = Field(title='Order type', form=True, model='order_type')
    store_id: UUID = Field(title='Store', table=True, form=True, model='store')
    location_src_id: Optional[UUID] = Field(default=None, title='Source Location', form=True, model='location')
    location_dest_id: Optional[UUID] = Field(default=None, title='Destination Location', form=True, model='location')
    location_type_src_id: Optional[UUID] = Field(default=None, title='Source Location Type', form=True,
                                                 model='location_type')
    location_type_dest_id: Optional[UUID] = Field(default=None, title='Destination Location Type', form=True,
                                                  model='location_type')
    partner_id: Optional[UUID] = Field(default=None, title='Partner', form=True, model='partner')
    origin_number: Optional[str] = Field(default=None, title='Original', form=True)
    planned_datetime: Optional[datetime] = Field(default=None, title='Planned Date', form=True)
    expiration_datetime: Optional[datetime] = Field(default=None, title='Expiration Date', form=False)
    description: Optional[str] = Field(default=None, title='Description', form=True)
    products: list[Product] = Field(default=[], title='Products', form=True)
    packages: list[Package] = Field(default=[], title='Packages', form=True)
