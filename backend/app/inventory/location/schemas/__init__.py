from pydantic import BaseModel

from .location_schemas import *
from .location_type_schemas import *


class ExceptionResponseSchema(BaseModel):
    error: str
