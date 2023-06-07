import uuid
from typing import TypeVar, Type, Optional, Generic

from sqlalchemy import select, update, delete

from core.db.session import Base, session
from core.repository.enum import SynchronizeSessionEnum
from core.db import Transactional, Propagation

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepo(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    @classmethod
    async def get_all(cls, limit: int=100) -> Optional[ModelType]:
        print(cls.__str__)
        query = select(cls.Config.model).limit(limit)
        result = await session.execute(query)
        return result.scalars().all()

    @classmethod
    async def get_by_id(cls, id: uuid.UUID) -> Optional[ModelType]:
        query = select(cls.Config.model).where(cls.Config.model.id == id.__str__())
        result = await session.execute(query)
        return result.scalars().first()
    async def save(
        self,
        params: dict,
        synchronize_session: SynchronizeSessionEnum = False,
    ) -> None:
        query = (
            update(self.Config.model)
            .where(self.Config.model.id == self.id)
            .values(**params)
            .execution_options(synchronize_session=synchronize_session)
        )
        await session.execute(query)

    async def delete(self) -> None:
        await session.delete(self.Config.model)

    async def delete_by_id(
        self,
        id: int,
        synchronize_session: SynchronizeSessionEnum = False,
    ) -> None:
        query = (
            delete(self.Config.model)
            .where(self.Config.model.id == id)
            .execution_options(synchronize_session=synchronize_session)
        )
        await session.execute(query)

    @Transactional(propagation=Propagation.REQUIRED)
    async def create(self) -> ModelType:
        entity = self.Config.model(**self.dict())
        saved = session.add(entity)
        return self.id

