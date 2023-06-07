import uuid

from pydantic import BaseModel, Field, UUID4
from core.repository.base import BaseRepo
from app.store.models import Store, StoreType
from typing import Optional


class StoreSchema(BaseModel, BaseRepo):
    """
    Упрощенный вид схема, когда подходит в целом и для работы и для API
    """
    id: Optional[UUID4] = Field(description="ID", default_factory=uuid.uuid4)
    title: str = Field(..., description="Title")
    external_id: str = Field(..., description="External ID")
    address: str = Field(..., description="Address")
    source: StoreType = Field(..., description="Source")

    class Config:
        orm_mode = True
        model = Store # Данная штука служит как бы для обращения к ORM
