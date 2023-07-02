from starlette.requests import Request

from app.basic.uom.schemas.uom_category_schemas import UomCategoryCreateScheme, UomCategoryUpdateScheme, \
    UomCategoryFilter
from app.basic.uom.schemas.uom_schemas import UomCreateScheme, UomUpdateScheme, UomFilter
from app.basic.uom.models.uom_category_models import UomCategory
from app.basic.uom.models.uom_models import Uom
from core.db.session import session
from core.service.base import BaseService


class UomCategoryService(BaseService[UomCategory, UomCategoryCreateScheme, UomCategoryUpdateScheme, UomCategoryFilter]):
    def __init__(self, request: Request, db_session: session = session):
        super(UomCategoryService, self).__init__(request, UomCategory, db_session)


class UomService(BaseService[Uom, UomCreateScheme, UomUpdateScheme, UomFilter]):
    def __init__(self, request: Request, db_session: session = session):
        super(UomService, self).__init__(request, Uom, db_session)
