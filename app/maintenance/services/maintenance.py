from app.maintenance.models.maintenance import (
    Contractor,
    ServiceSupplier,
    Manufacturer,
    Model,
    AssetType,
    Asset,
    AssetLog,
    Order,
    OrderLine
)
from app.maintenance.schemas.contractor import ContractorCreateScheme, ContractorUpdateScheme
from app.maintenance.schemas.service_supplier import ServiceSupplierCreateScheme, ServiceSupplierUpdateScheme
from app.maintenance.schemas.manufacturer import ManufacturerCreateScheme, ManufacturerUpdateScheme
from app.maintenance.schemas.model import ModelCreateScheme, ModelUpdateScheme
from app.maintenance.schemas.asset_type import AssetTypeCreateScheme, AssetTypeUpdateScheme
from app.maintenance.schemas.asset import AssetCreateScheme, AssetUpdateScheme
from app.maintenance.schemas.asset_log import AssetLogCreateScheme, AssetLogUpdateScheme
from app.maintenance.schemas.order import OrderCreateScheme, OrderUpdateScheme, OrderLineCreateScheme, \
    OrderLineUpdateScheme
from core.db.session import session
from core.service.base import BaseService


class ContractorService(BaseService[Contractor, ContractorCreateScheme, ContractorUpdateScheme]):
    def __init__(self, db_session: session = session):
        super(ContractorService, self).__init__(Contractor, db_session)


class ServiceSupplierService(BaseService[ServiceSupplier, ServiceSupplierCreateScheme, ServiceSupplierUpdateScheme]):
    def __init__(self, db_session: session = session):
        super(ServiceSupplierService, self).__init__(ServiceSupplier, db_session)


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
