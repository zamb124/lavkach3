from pydantic import BaseModel

from .product_storage_type_schemas import *
from .storage_type_schemas import *


class ExceptionResponseSchema(BaseModel):
    error: str
