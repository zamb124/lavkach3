from pydantic import BaseModel
from pydantic.types import UUID4, Optional

from backend.app.maintenance.models import AssetLogAction
from backend.core.schemas.timestamps import TimeStampScheme


class AssetLogBaseScheme(BaseModel):
    asset_id: UUID4
    action: AssetLogAction
    from_: Optional[str]
    to: Optional[str]


class AssetLogUpdateScheme(AssetLogBaseScheme):
    pass


class AssetLogCreateScheme(AssetLogBaseScheme):
    pass


class AssetLogScheme(AssetLogCreateScheme, TimeStampScheme):
    id: UUID4
    lsn: int

    class Config:
        orm_mode = True
