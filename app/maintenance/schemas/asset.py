from datetime import datetime
from typing import List, Optional
import uuid
from pydantic import BaseModel, Field, HttpUrl, conint
from pydantic.types import UUID4, condecimal, constr
from app.to_camel import to_camel
from app.maintenance.models import Asset, Type, SourceType, AssetStatus
from core.repository.base import BaseRepo
from app.maintenance.schemas.asset_type import AssetTypeScheme
from app.maintenance.schemas.manufacturer import ManufacturerScheme
from app.maintenance.schemas.model import ModelScheme
from app.user.schemas import GetUserListResponseSchema
from app.store.schemas import StoreSchema


class AssetBaseScheme(BaseModel, BaseRepo):
    title: str = Field(description="Title")
    company_id: UUID4
    asset_type_id: UUID4
    manufacturer_id: UUID4
    store_id: UUID4
    model_id: UUID4
    status: AssetStatus
    serial: str
    at:str
    user_id: UUID4
    barcode: UUID4

    class Config:
        model = Asset
class AssetUpdateScheme(AssetBaseScheme):
    pass
class AssetCreateScheme(AssetBaseScheme):
    class Config:
        model = Asset
class AssetScheme(AssetCreateScheme):
    id: UUID4
    lsn: int
    asset_type: AssetTypeScheme
    manufacturer: ManufacturerScheme
    store: StoreSchema
    model: ModelScheme
    user: GetUserListResponseSchema
    class Config:
        model = Asset
        orm_mode = True
        #alias_generator = to_camel
        #allow_population_by_field_name = True