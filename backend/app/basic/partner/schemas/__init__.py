from .partner_schemas import *
from pydantic import BaseModel


class ExceptionResponseSchema(BaseModel):
    error: str
