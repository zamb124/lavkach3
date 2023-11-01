import uuid

from pydantic import BaseModel, UUID4
from typing import Optional, List
from sqlalchemy import select
from core.db.session import session

from app.basic.user.models import User


class CurrentUser(BaseModel):
    id: Optional[UUID4] = None
    companies: Optional[List[UUID4]] = []
    roles: Optional[List[str]] = []
    is_admin: Optional[bool] = False

    class Config:
        validate_assignment = True

    async def get_user_data(self):
        query = select(User).where(User.id == self.id)
        result = await session.execute(query)
        return result.scalars().first()
