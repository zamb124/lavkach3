from core.repository.base import BaseRepo
from app.maintenance.models import AssetLog
from pydantic import BaseModel
from pydantic.types import UUID4
from app.maintenance.models import AssetLogAction


class AssetLogBaseScheme(BaseModel, BaseRepo):
    asset_id: UUID4
    action: AssetLogAction
    from_: str
    to: str

    class Config:
        model = AssetLog
