from .product_schemas import *
from .product_category_schemas import *


class ExceptionResponseSchema(BaseModel):
    error: str
