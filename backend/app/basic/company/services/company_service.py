from app.basic.company.models.company_models import Company
from app.basic.company.schemas.company_schemas import CompanyCreateScheme, CompanyUpdateScheme
from core.db.session import session, get_async_session
from core.service.base import BaseService
from fastapi import Depends
from sqlalchemy import select

Deny = 'Deny'

class CompanyService(BaseService[Company, CompanyCreateScheme, CompanyUpdateScheme]):
    def __init__(self, request, db_session=session):
        super(CompanyService, self).__init__(request, Company, db_session)


    async def list(self, limit: int, cursor: int = 0):
        query = (
            select(self.model)
            .where(self.model.lsn > cursor).limit(limit)  # .filter(self.model.id.in_(self.companies))
        )
        result = await self.session.execute(query)
        return result.scalars().all()
