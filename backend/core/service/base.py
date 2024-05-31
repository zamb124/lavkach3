import uuid
import logging
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Generic, Optional, Type, TypeVar
from uuid import uuid4

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import BaseModel
from sqlalchemy import select, Row, RowMapping, inspect
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.exceptions import HTTPException

from core.db.session import Base, session
from core.fastapi.middlewares.authentication import CurrentUser
from core.schemas import BaseFilter

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
FilterSchemaType = TypeVar("FilterSchemaType", bound=Filter)
before_fields = ['role_ids', 'company_ids', 'is_admin', 'store_id']

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Model:
    service: object
    model: object


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


class LocalCache:

    def __init__(self):
        self._data = defaultdict(defaultdict)


localcache = LocalCache()


class BaseCache:
    service: 'BaseService'

    def __init__(self, service: 'BaseService'):
        self.service = service
        self.cache = localcache._data

    def get(self, id: uuid.UUID):
        return self.cache[self.service.model.__tablename__].get(id)

    def set(self, sql_obj:list | object):
        if isinstance(sql_obj, list):
            for obj in sql_obj:
                self.set(obj)
            return sql_obj
        self.cache[self.service.model.__tablename__][sql_obj.id] = sql_obj  # type: ignore
        return sql_obj.id  # type: ignore

    def delete(self, id: uuid.UUID):
        self.cache[self.service.model.__tablename__].pop(id, False)
        return True


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
        else:
            self.user = request.user
        self.model = model
        self.create_schema = create_schema
        self.update_schema = update_schema
        self.request = request
        self.env = request.scope['env']
        self.session = db_session if db_session else session
        self.basecache = BaseCache(self)

    def sudo(self):
        self.user = CurrentUser(id=uuid4(), is_admin=True)
        return self

    async def _get(self, id: Any) -> Row | RowMapping:
        query = select(self.model).where(self.model.id == id)
        if self.user.is_admin:
            query = select(self.model).where(self.model.id == id)
        result = await self.session.execute(query)
        entity = result.scalars().first()
        if not entity:
            raise HTTPException(status_code=404, detail=f"Not found")
        return entity

    async def get(self, id: Any) -> Row | RowMapping:
        entity = None
        if not entity:
            entity = await self._get(id)
            #self.basecache.set(entity)
        insp = inspect(entity)
        if not insp.persistent:
            self.session.add(entity)
            await self.session.refresh(entity)

        return entity

    async def _list(self, _filter: FilterSchemaType | dict, size: int):
        if not isinstance(_filter, BaseFilter):
            if isinstance(_filter, dict):
                _filter = self.env[self.model.__tablename__].schemas.filter(**_filter)
        if self.model.__tablename__ not in ('company', 'user'):
            setattr(_filter, 'company_id__in', [self.user.company_id])
        query_filter = _filter.filter(select(self.model)).limit(size)  # type: ignore
        if getattr(_filter, 'order_by'):
            query_filter = _filter.sort(query_filter)  # type: ignore
        executed_data = await self.session.execute(query_filter)
        result = executed_data.scalars().all()
        return result

    async def list(self, _filter: FilterSchemaType | dict, size: int = 100):
        entitys = await self._list(_filter, size)
        #self.basecache.set(entitys)
        return entitys

    async def _create(self, obj: CreateSchemaType | dict, commit=True) -> ModelType:
        if isinstance(obj, dict):
            try:
                obj = self.create_schema(**obj)
            except Exception as ex:
                raise HTTPException(status_code=422, detail=str(ex))
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
                    pass  # TODO: дописать такую логику где не list а model
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
                    await self.session.refresh(entity)
                    setattr(_rel_dump, f'{self.model.__tablename__}_id', entity.id)
                    await _rel_method(obj=_rel_dump, commit=True, parent=entity)
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

    async def create(self, obj: CreateSchemaType | dict, commit=True) -> ModelType:
        entity = await self._create(obj, commit=commit)
        #self.basecache.set(entity)
        return entity

    async def _update(self, id: Any, obj: UpdateSchemaType, commit=True) -> Optional[ModelType]:
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
                            await self.session.refresh(rel_entity)
                        else:
                            _dump = _obj.model_dump()
                            _dump[f'{self.model.__tablename__}_id'] = id
                            create_obj = rel.create_schema(**_dump)
                            await rel.create(obj=create_obj, parent=entity, commit=False)
                else:
                    to_set.append((key, value))
        for k, v in to_set:
            setattr(entity, k, v)
        # entity.mode_list_rel = new_entity.move_list_rel
        try:
            self.session.add(entity)
        except InvalidRequestError as ex:
            logger.warning(ex)
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
        self.session.expire_all()
        return entity

    async def update(self, id: Any, obj: UpdateSchemaType, commit=True) -> Optional[ModelType]:
        entity = await self._update(id, obj, commit=True)
        #self.basecache.set(entity)
        return entity

    async def _delete(self, id: Any) -> bool:
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

    async def delete(self, id: Any) -> bool:
        #self.basecache.delete(id)
        res = await self._delete(id)
        return res
