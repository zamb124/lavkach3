import uuid

from pydantic import BaseModel, UUID4, computed_field
from typing import Optional, List
from sqlalchemy import select
from core.db.session import session

#from app.basic.user.models import User
from core.types import TypeLocale


class CurrentUser(BaseModel):
    user_id: Optional[UUID4] = None
    company_ids: Optional[List[UUID4]] = []
    company_id: Optional[UUID4] = False
    store_id: Optional[UUID4] = False
    role_ids: Optional[List[str]] = []
    is_admin: Optional[bool] = False
    locale: Optional[TypeLocale] = False
    nickname: Optional[str] = None
    email: Optional[str] = None

    class Config:
        validate_assignment = True

    @computed_field
    @property
    def id(self) -> str:
        return self.user_id

    async def get_user_data(self):
        query = select(User).where(User.id == self.id)
        result = await session.execute(query)
        return result.scalars().first()
