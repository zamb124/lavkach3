from starlette.requests import Request

from app.basic.store.models.store_models import Store
from app.basic.store.schemas.store_schemas import StoreCreateScheme, StoreUpdateScheme, StoreFilter
from core.db.session import session
from core.service.base import BaseService


class StoreService(BaseService[Store, StoreCreateScheme, StoreUpdateScheme, StoreFilter]):
    def __init__(self, request: Request, db_session: session=session):
        super(StoreService, self).__init__(request, Store, db_session)


