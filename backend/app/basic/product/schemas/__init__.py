from .product_schemas import *
from .product_category_schemas import *
from .product_storage_type_schemas import *


class ExceptionResponseSchema(BaseModel):
    error: str
