from app.maintenance.models import AssetLog
from pydantic import BaseModel
from pydantic.types import UUID4, Optional
from app.maintenance.models import AssetLogAction
from core.schemas.timestamps import TimeStampScheme

class AssetLogBaseScheme(BaseModel):
    asset_id: UUID4
    action: AssetLogAction
    from_: Optional[str]
    to: Optional[str]


class AssetTypeUpdateScheme(AssetLogBaseScheme):
    pass


class AssetTypeCreateScheme(AssetLogBaseScheme):
    pass


class AssetTypeScheme(AssetTypeCreateScheme, TimeStampScheme):
    id: UUID4
    lsn: int

    class Config:
        orm_mode = True
