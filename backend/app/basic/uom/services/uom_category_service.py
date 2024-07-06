from starlette.requests import Request

from app.basic.uom.models.uom_category_models import UomCategory
from app.basic.uom.schemas.uom_category_schemas import UomCategoryCreateScheme, UomCategoryUpdateScheme, \
    UomCategoryFilter
from core.service.base import BaseService


class UomCategoryService(BaseService[UomCategory, UomCategoryCreateScheme, UomCategoryUpdateScheme, UomCategoryFilter]):
    def __init__(self, request:Request):
        super(UomCategoryService, self).__init__(request, UomCategory,UomCategoryCreateScheme, UomCategoryUpdateScheme)


