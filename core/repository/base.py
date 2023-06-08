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
    async def update(
        self,
        id: uuid.UUID,
        synchronize_session: SynchronizeSessionEnum = False,
    ) -> None:
        query = (
            update(self.Config.model)
            .where(self.Config.model.id == id.__str__())
            .values(**self.dict())
            .execution_options(synchronize_session=synchronize_session)
        )
        print(query)
        await session.execute(query)
        await session.commit()
        #await session.refresh(entity)
        entity = await self.get_by_id(id.__str__())
        return entity
    async def delete(self) -> None:
        await session.delete(self.Config.model)

    @classmethod
    async def delete_by_id(
        cls,
        id: uuid.UUID,
        synchronize_session: SynchronizeSessionEnum = False,
    ) -> None:
        query = (
            delete(cls.Config.model)
            .where(cls.Config.model.id == id.__str__())
            .execution_options(synchronize_session=synchronize_session)
        )
        await session.execute(query)
        await session.commit()
    #@Transactional(propagation=Propagation.REQUIRED)
    async def create(self) -> ModelType:
        entity = self.Config.model(**self.dict())
        #entity.id = uuid.uuid4()
        session.add(entity)
        await session.commit()
        await session.refresh(entity)
        return entity

