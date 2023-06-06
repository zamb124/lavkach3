from typing import Optional, List

from sqlalchemy import or_, select, and_

from app.company.models import Company
from app.user.schemas.user import LoginResponseSchema
from core.db import Transactional, Propagation, session
from core.exceptions import (
    PasswordDoesNotMatchException,
    DuplicateEmailOrNicknameException,
    UserNotFoundException,
)
from core.utils.token_helper import TokenHelper


class CompanyService:
    def __init__(self):
        ...

    async def get_company_list(
        self,
        limit: int = 12,
    ) -> List[Company]:
        query = select(Company)
        query = query.limit(limit)
        result = await session.execute(query)
        return result.scalars().all()

    @Transactional(propagation=Propagation.REQUIRED)
    async def create_user(self, email: str, password1: str, password2: str, nickname: str) -> None:
        result = await session.execute(query)

        user = User(email=email, password=password1, nickname=nickname)
        session.add(user)
