from pydantic import BaseModel

from .store_staff_schemas import *


class ExceptionResponseSchema(BaseModel):
    error: str
