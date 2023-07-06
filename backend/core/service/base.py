from typing import Any, Generic, List, Optional, Type, TypeVar, Dict, Sequence
from functools import wraps
from uuid import uuid4

from pydantic import BaseModel
from starlette.exceptions import HTTPException
from starlette.requests import Request

from app.basic.user.schemas import UserCreateScheme
from core.db.session import Base, session
from sqlalchemy import select, Row, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi_filter.contrib.sqlalchemy import Filter
from core.fastapi.middlewares.authentication import CurrentUser
import math

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
FilterSchemaType = TypeVar("FilterSchemaType", bound=Filter)
before_fields = ['roles', 'companies', 'is_admin', 'store_id']


class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType, FilterSchemaType]):
    def __init__(self, request: Request | CurrentUser | None = None, model: Type[ModelType] = None, db_session: AsyncSession = session):
        if isinstance(request, CurrentUser):
            self.user = CurrentUser
        elif isinstance(request, Request):
            self.user = request.user
        self.model = model
        self.session = db_session

    def sudo(self):
        self.user = CurrentUser(id=uuid4(), is_admin=True)
        return self

    async def get(self, id: Any) -> Optional[ModelType]:
        query = select(self.model).where(self.model.id == id)
        if self.user.is_admin:
            query = select(self.model).where(self.model.id == id)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def list(self, _filter: FilterSchemaType, size: int):
        query_filter = _filter.filter(select(self.model)).limit(size)
        executed_data = await self.session.execute(query_filter)
        return executed_data.scalars().all()

    async def create(self, obj: CreateSchemaType) -> ModelType:
        entity = self.model(**obj.dict())
        self.session.add(entity)
        try:
            await self.session.commit()
            await self.session.refresh(entity)
        except IntegrityError as e:
            await self.session.rollback()
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
        self.session.add(entity)
        for column, value in obj.dict(exclude_unset=True).items():
            setattr(entity, column, value)
        try:
            await self.session.commit()
            await self.session.refresh(entity)
        except IntegrityError as e:
            await self.session.rollback()
            if "duplicate key" in str(e):
                raise HTTPException(status_code=409, detail=f"Conflict Error entity {str(e)}")
            else:
                raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"ERROR:  {str(e)}")
        return entity

    async def delete(self, id: Any) -> None:
        entity = await self.get(id)
        await self.session.delete(entity)
        try:
            await self.session.commit()
        except IntegrityError as e:
            await self.session.rollback()
            if "duplicate key" in str(e):
                raise HTTPException(status_code=409, detail=f"Conflict Error entity {str(e)}")
            else:
                raise e
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"ERROR:  {str(e)}")
        return entity
