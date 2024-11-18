from pydantic import BaseModel

from .store_schemas import *


class ExceptionResponseSchema(BaseModel):
    error: str
