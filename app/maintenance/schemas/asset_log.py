from core.repository.base import BaseRepo
from app.maintenance.models import AssetLog
from pydantic import BaseModel
from pydantic.types import UUID4, Optional
from app.maintenance.models import AssetLogAction


class AssetLogBaseScheme(BaseModel, BaseRepo):
    asset_id: UUID4
    action: AssetLogAction
    from_: Optional[str]
    to: Optional[str]

    class Config:
        model = AssetLog
        orm_mode = True
