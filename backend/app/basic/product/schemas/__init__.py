from pydantic import BaseModel

from .product_category_schemas import *
from .product_schemas import *


class ExceptionResponseSchema(BaseModel):
    error: str
