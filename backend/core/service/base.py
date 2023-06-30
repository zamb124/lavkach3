from typing import Any, Generic, List, Optional, Type, TypeVar
from functools import wraps
from pydantic import BaseModel
from starlette.exceptions import HTTPException
from starlette.requests import Request

from core.db.session import Base, session
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
before_fields = ['roles', 'companies', 'is_admin', 'store_id']


class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, request: Request, model: Type[ModelType], db_session: AsyncSession):
        self.request = request
        self.companies = request.user.companies or []
        self.model = model
        self.session = db_session

    # Теперь декорируем любую нужную функцию нашим новеньким, ещё блестящим декоратором:

    async def get(self, id: Any) -> Optional[ModelType]:
        query = select(self.model).where(self.model.id == id).filter(self.model.company_id.in_(self.companies))
        if self.request.user.is_admin:
            query = select(self.model).where(self.model.id == id)
        result = await session.execute(query)
        return result.scalars().first()

    async def list(self, limit: int, cursor: int=0) -> List[ModelType]:
        query = (
            select(self.model)
            .where(self.model.lsn > cursor).limit(limit).
            filter(self.model.company_id.in_(self.companies))
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def create(self, obj: CreateSchemaType) -> ModelType:
        entity = self.model(**obj.dict())
        #entity.id = uuid.uuid4()
        session.add(entity)
        try:
            await session.commit()
            await session.refresh(entity)
        except IntegrityError as e:
            await session.rollback()
            if "duplicate key" in str(e):
                raise HTTPException(status_code=409, detail=f"Conflict Error entity {str(e)}")
            else:
                raise e
        except Exception as e:
            raise HTTPException(status_code=409, detail=f"Conflict Error entity {str(e)}")
        return entity

    async def update(self, id: Any, obj: UpdateSchemaType) -> Optional[ModelType]:
        entity = await self.get(id)
        if not entity:
            raise HTTPException(status_code=404, detail=f"Not Found with id {id}")
        session.add(entity)
        for column, value in obj.dict(exclude_unset=True).items():
            setattr(entity, column, value)
        try:
            await session.commit()
            await session.refresh(entity)
        except IntegrityError as e:
            await session.rollback()
            if "duplicate key" in str(e):
                raise HTTPException(status_code=409, detail=f"Conflict Error entity {str(e)}")
            else:
                raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"ERROR:  {str(e)}")
        return entity

    async def delete(self, id: Any) -> None:
        entity = await self.get(id)
        await session.delete(entity)
        try:
            await session.commit()
        except IntegrityError as e:
            await session.rollback()
            if "duplicate key" in str(e):
                raise HTTPException(status_code=409, detail=f"Conflict Error entity {str(e)}")
            else:
                raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"ERROR:  {str(e)}")
        return entity