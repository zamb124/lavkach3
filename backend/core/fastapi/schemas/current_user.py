import uuid

from pydantic import BaseModel, UUID4
from typing import Optional, List
from sqlalchemy import select
from core.db.session import session

from app.basic.user.models import User
from core.types import TypeLocale


class CurrentUser(BaseModel):
    user_id: Optional[UUID4] = None
    companies: Optional[List[UUID4]] = None
    roles: Optional[List[str]] = []
    is_admin: Optional[bool] = False
    locale: Optional[TypeLocale] = False

    class Config:
        validate_assignment = True

    async def get_user_data(self):
        query = select(User).where(User.id == self.id)
        result = await session.execute(query)
        return result.scalars().first()
