
from pydantic import BaseModel
from pydantic.types import UUID4
from app.maintenance.models import AssetLog, AssetStatus
#from app.maintenance.schemas.asset import AssetScheme
from core.repository.base import BaseRepo
from app.store.schemas import StoreSchema


class AssetLogBaseScheme(BaseModel, BaseRepo):
    asset_id:UUID4
    serial: str
    at: str
    store_id: UUID4
    status: AssetStatus
    barcode: UUID4

    class Config:
        model = AssetLog
class AssetLogUpdateScheme(AssetLogBaseScheme):
    pass
class AssetLogCreateScheme(AssetLogBaseScheme):
    class Config:
        model = AssetLog
class AssetLogScheme(AssetLogCreateScheme):
    id: UUID4
    lsn: int
    store: StoreSchema
    #asset: AssetScheme
    class Config:
        model = AssetLog
        orm_mode = True
        #alias_generator = to_camel
        #allow_population_by_field_name = True