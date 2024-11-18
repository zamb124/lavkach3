from pydantic import BaseModel

from .lot_schemas import *
from .quants_schemas import *


class ExceptionResponseSchema(BaseModel):
    error: str
