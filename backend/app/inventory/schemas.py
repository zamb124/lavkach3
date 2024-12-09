from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, model_validator, ValidationError

from app.inventory.location.enums import LocationClass, PhysicalStoreLocationClass
from app.inventory.order import MoveCreateScheme, OrderTypeScheme, MoveScheme
from app.inventory.quant import QuantScheme
from core.schemas.basic_schemes import BasicField as Field, BasicModel


class CreateMovementsError(ValueError):
    ...


class Quant(QuantScheme):
    order_types: Optional[list[OrderTypeScheme]] = Field(default=[], title='Order Types', form=True, model='order_type')
    qty_to_move: Optional[float] = Field(default=0.0, title='Quantity to move', form=True)
    location_dest_id: Optional[UUID] = Field(default=None, title='Destination Location', form=True, model='location')


class Product(BasicModel):
    product_id: UUID = Field(title='Product', form=True, model='product')
    quantity: float = Field(title='Quantity', form=True, gt=0)
    avaliable_quantity: float = Field(default=0.0, title='Avaliable Quantity', form=True)
    lot_id: Optional[UUID] = Field(default=None, title='Lot', form=True, model='lot')
    uom_id: Optional[UUID] = Field(default=None, title='UOM', form=True, model='uom')
    quants: Optional[list[Quant]] = Field(default=[], title='Quants', form=True)
    moves_to_create: Optional[list[MoveCreateScheme]] = Field(default=[], title='Moves to create', form=True, model='move')
    moves_created: Optional[list[MoveScheme]] = Field(default=[], title='Moves created', form=True, model='move')


class Package(BasicModel):
    package_id: UUID = Field(title='Package', form=True, model='location',
                             filter={'location_class__in': LocationClass.PACKAGE.value})
    quants: Optional[list[Quant]] = Field(default=[], title='Quants', form=True)
    moves_to_create: Optional[list[MoveCreateScheme]] = Field(default=[], title='Moves', form=True, model='move')
    moves_created: Optional[list[MoveScheme]] = Field(default=[], title='Moves created', form=True, model='move')

class CreateMovements(BasicModel):
    filled: bool = Field(default=False, title='Filled', form=False)
    commit: bool = Field(default=False, title='Commit', form=False)
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

    @model_validator(mode='before')
    def check_at_least_one_field(cls, values):
        if not any(values.get(field) for field in
                   ['location_src_zone_id', 'location_src_id', 'location_type_src_id', 'products', 'packages']):
            raise CreateMovementsError(
                'At least one of location_src_zone_id, location_src_id, location_type_src_id, products, or packages must be provided.')
        return values
