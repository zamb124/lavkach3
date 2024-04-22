import logging
from datetime import datetime
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


from core.utils.timeit import timed

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
FilterSchemaType = TypeVar("FilterSchemaType", bound=Filter)
before_fields = ['role_ids', 'company_ids', 'is_admin', 'store_id']

def import_service(service_name):
    components = service_name.split('.')
    mod = __import__(components[0])
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod

def is_pydantic(obj: object | list):
    """ Checks whether an object is pydantic. """
    if isinstance(obj, list):
        for i in obj:
            return type(i).__class__.__name__ == "ModelMetaclass"
    return type(obj).__class__.__name__ == "ModelMetaclass"


def model_to_entity(schema):
    """
        Iterates through pydantic schema and parses nested schemas
        to a dictionary containing SQLAlchemy models.
        Only works if nested schemas have specified the Meta.orm_model.
    """
    if is_pydantic(schema):
        try:
            converted_model = model_to_entity(dict(schema))
            return schema.Config.orm_model(**converted_model)
        except AttributeError:
            model_name = schema.__class__.__name__
            raise AttributeError(f"Failed converting pydantic model: {model_name}.Meta.orm_model not specified.")

    elif isinstance(schema, list):
        return [model_to_entity(model) for model in schema]

    elif isinstance(schema, dict):
        for key, model in schema.items():
            schema[key] = model_to_entity(model)

    return schema

class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType, FilterSchemaType]):
    def __init__(
            self,
            request,
            model: Type[ModelType],
            create_schema: Type[CreateSchemaType],
            update_schema: Type[UpdateSchemaType],
            db_session: AsyncSession = session,

    ):
        if isinstance(request, CurrentUser):
            self.user = CurrentUser
        elif isinstance(request, Request):
            self.user = request.user
        self.model = model
        self.create_schema = create_schema
        self.update_schema = update_schema
        self.request = request
        self.session = db_session if db_session else session

    def sudo(self):
        self.user = CurrentUser(id=uuid4(), is_admin=True)
        return self

    async def get(self, id: Any) -> Row | RowMapping:
        query = select(self.model).where(self.model.id == id)
        if self.user.is_admin:
            query = select(self.model).where(self.model.id == id)
        result = await self.session.execute(query)
        sql_obj = result.scalars().first()
        if not sql_obj:
            raise HTTPException(status_code=404, detail=f"Not found")
        return sql_obj

    @timed
    async def list(self, _filter: FilterSchemaType, size: int):
        if self.model.__tablename__ not in ('company', 'user'):
            setattr(_filter, 'company_id__in', [self.user.company_id])
        query_filter = _filter.filter(select(self.model)).limit(size)
        if getattr(_filter, 'order_by'):
            query_filter = _filter.sort(query_filter)
        executed_data = await self.session.execute(query_filter)
        result = executed_data.scalars().all()
        return result

    @timed
    async def create(self, obj: CreateSchemaType, commit=True) -> ModelType:
        to_set = []
        exclude_rel = []
        relcations_to_create = []
        for key, value in obj.__dict__.items():
            if is_pydantic(value):
                if isinstance(value, list):
                    for _obj in value:
                        rel_service = import_service(_obj.Config.service)
                        rel = rel_service(self.request)
                        if hasattr(_obj, 'id'):
                            rel_entity = await rel.update(id=_obj.id, obj=_obj, commit=False)
                        else:
                            _dump = _obj.model_dump()
                            create_obj = rel.create_schema(**_dump)
                            relcations_to_create.append((rel.create, create_obj))
                        exclude_rel.append(key)
                else:
                    pass # TODO: дописать такую логику где не list а model
            else:
                to_set.append((key, value))
        entity = self.model(**obj.model_dump(exclude=exclude_rel))
        entity.company_id = self.user.company_id
        self.session.add(entity)
        if commit:
            try:
                await self.session.commit()
                await self.session.refresh(entity)
                for _rel_method, _rel_dump in relcations_to_create:
                    setattr(_rel_dump, 'order_id', entity.id)
                    await _rel_method(obj=_rel_dump, commit=True)
                await self.session.refresh(entity)
            except IntegrityError as e:
                await self.session.rollback()
                if "duplicate key" in str(e):
                    raise HTTPException(status_code=409, detail=f"Conflict Error entity {str(e)}")
                else:
                    raise HTTPException(status_code=500, detail=f"ERROR:  {str(e)}")
            except Exception as e:
                raise HTTPException(status_code=409, detail=f"Conflict Error entity {str(e)}")
        else:
            await self.session.flush([entity])

        return entity


    @timed
    async def update(self, id: Any, obj: UpdateSchemaType, commit=True) -> Optional[ModelType]:
        entity = await self.get(id)
        if not entity:
            raise HTTPException(status_code=404, detail=f"Not Found with id {id}")

        to_set = []
        for key, value in obj.__dict__.items():
            if key in obj.model_fields_set:
                obj_value = getattr(obj, key)
                if is_pydantic(obj_value):
                    for _obj in obj_value:
                        rel_service = import_service(_obj.Config.service)
                        rel = rel_service(self.request)
                        if _obj.id:
                            rel_entity = await rel.update(id=_obj.id, obj=_obj, commit=False)
                        else:
                            _dump = _obj.model_dump()
                            _dump[f'{self.model.__tablename__}_id'] = id
                            create_obj = rel.create_schema(**_dump)
                            rel_entity = await rel.create(obj=create_obj, commit=False)
                        self.session.add(rel_entity)
                else:
                    to_set.append((key, value))
        for k, v in to_set:
            setattr(entity, k, v)
        #entity.mode_list_rel = new_entity.move_list_rel
        self.session.add(entity)
        if commit:
            try:
                await self.session.commit()
                await self.session.refresh(entity)
            except IntegrityError as e:
                await self.session.rollback()
                if "duplicate key" in str(e):
                    raise HTTPException(status_code=409, detail=f"Conflict Error entity {str(e)}")
                else:
                    raise HTTPException(status_code=500, detail=f"ERROR:  {str(e)}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"ERROR:  {str(e)}")
        else:
            await self.session.flush([entity])
        return entity

    @timed
    async def delete(self, id: Any):
        entity = await self.get(id)
        await self.session.delete(entity)
        try:
            await self.session.commit()
        except IntegrityError as e:
            await self.session.rollback()
            if "duplicate key" in str(e):
                raise HTTPException(status_code=409, detail=f"Conflict Error entity {str(e)}")
            else:
                raise HTTPException(status_code=500, detail=f"ERROR:  {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"ERROR:  {str(e)}")
        return True

