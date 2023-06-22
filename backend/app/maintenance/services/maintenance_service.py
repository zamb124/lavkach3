from app.maintenance.models.maintenance_models import (
    Manufacturer,
    Model,
    AssetType,
    Asset,
    AssetLog,
    Order,
    OrderLine
)
from app.maintenance.schemas.manufacturer_schemas import ManufacturerCreateScheme, ManufacturerUpdateScheme
from app.maintenance.schemas.model_schemas import ModelCreateScheme, ModelUpdateScheme
from app.maintenance.schemas.asset_type_schemas import AssetTypeCreateScheme, AssetTypeUpdateScheme
from app.maintenance.schemas.asset_schemas import AssetCreateScheme, AssetUpdateScheme
from app.maintenance.schemas.asset_log_schemas import AssetLogCreateScheme, AssetLogUpdateScheme
from app.maintenance.schemas.order_schemas import OrderCreateScheme, OrderUpdateScheme, OrderLineCreateScheme, \
    OrderLineUpdateScheme
from core.db.session import session
from core.service.base import BaseService


class ManufacturerService(BaseService[Manufacturer, ManufacturerCreateScheme, ManufacturerUpdateScheme]):
    def __init__(self, db_session: session = session):
        super(ManufacturerService, self).__init__(Manufacturer, db_session)


class ModelService(BaseService[Model, ModelCreateScheme, ModelUpdateScheme]):
    def __init__(self, db_session: session = session):
        super(ModelService, self).__init__(Model, db_session)


class AssetTypeService(BaseService[AssetType, AssetTypeCreateScheme, AssetTypeUpdateScheme]):
    def __init__(self, db_session: session = session):
        super(AssetTypeService, self).__init__(AssetType, db_session)


class AssetService(BaseService[Asset, AssetCreateScheme, AssetUpdateScheme]):
    def __init__(self, db_session: session = session):
        super(AssetService, self).__init__(Asset, db_session)


class AssetLogService(BaseService[AssetLog, AssetLogCreateScheme, AssetLogUpdateScheme]):
    def __init__(self, db_session: session = session):
        super(AssetLogService, self).__init__(AssetLog, db_session)


class OrderService(BaseService[Order, OrderCreateScheme, OrderUpdateScheme]):
    def __init__(self, db_session: session = session):
        super(OrderService, self).__init__(Order, db_session)


class OrderLineService(BaseService[OrderLine, OrderLineCreateScheme, OrderLineUpdateScheme]):
    def __init__(self, db_session: session = session):
        super(OrderLineService, self).__init__(OrderLine, db_session)
