from datetime import datetime
from core.repository.enum import SynchronizeSessionEnum
import uuid
from typing import TypeVar
from pydantic import BaseModel, Field, HttpUrl, conint
from pydantic.types import UUID4, condecimal, constr
from app.to_camel import to_camel
from core.db.session import Base, session
from sqlalchemy import update
from app.maintenance.models import Asset, Type, SourceType, AssetStatus
from core.repository.base import BaseRepo
from app.maintenance.schemas.asset_type import AssetTypeScheme
from app.maintenance.schemas.manufacturer import ManufacturerScheme
from app.maintenance.schemas.model import ModelScheme
from app.user.schemas import GetUserListResponseSchema
from app.store.schemas import StoreSchema
from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException
from app.maintenance.models.maintenance import AssetLog
from core.db import Transactional


ModelType = TypeVar("ModelType", bound=Base)


class AssetLo(BaseRepo):
    async def create(self) -> ModelType:
        entity = self.Config.model(**self.dict())
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
        else:
            log = AssetLog(
                asset_id=entity.id,
                action='init',
                from_=None,
                to=None,
            )
            session.add(log)
            await session.commit()
            await session.refresh(entity)

        return entity

    async def update(
        self,
        id: uuid.UUID,
        synchronize_session: SynchronizeSessionEnum = False,
    ) -> None:
        entity = await self.get_by_id(id.__str__())

        query = (
            update(self.Config.model)
            .where(self.Config.model.id == id.__str__())
            .values(**self.dict())
            .execution_options(synchronize_session=synchronize_session)
        )
        await session.execute(query)
        changes = dict(self)
        if 'store_id' in changes and entity.store_id != changes['store_id']:
            log = AssetLog(
                asset_id=id,
                action='store_id',
                from_=str(entity.store_id),
                to=str(changes['store_id']),
            )
            session.add(log)
        if 'status' in changes and entity.status != changes['status']:
            log = AssetLog(
                asset_id=id,
                action='status',
                from_=str(entity.store_id),
                to=str(changes['status']),
            )
            session.add(log)
        if 'at' in changes and entity.at != changes['at']:
            if 'entry' in entity.at and entity.at['entry'] == 'courier':
                log = AssetLog(
                    asset_id=id,
                    action='at.courier',
                    from_=str(entity.at.get('id')),
                    to=str(changes['at'].get('id')),
                )
                session.add(log)
        await session.commit()
        #await session.refresh(entity)
        entity = await self.get_by_id(id.__str__())
        return entity


class AssetBaseScheme(BaseModel, AssetLo):
    title: str = Field(description="Title")
    company_id: UUID4
    asset_type_id: UUID4
    manufacturer_id: UUID4
    store_id: UUID4
    model_id: UUID4
    status: AssetStatus
    serial: str
    at:dict
    user_id: UUID4
    barcode: str

    class Config:
        model = Asset
class AssetUpdateScheme(AssetBaseScheme):
    pass
class AssetCreateScheme(AssetBaseScheme):
    class Config:
        model = Asset
class AssetScheme(AssetCreateScheme):
    id: UUID4
    lsn: int
    asset_type: AssetTypeScheme
    manufacturer: ManufacturerScheme
    store: StoreSchema
    model: ModelScheme
    user: GetUserListResponseSchema
    class Config:
        model = Asset
        orm_mode = True
        #alias_generator = to_camel
        #allow_population_by_field_name = True