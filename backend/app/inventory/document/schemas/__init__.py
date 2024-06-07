from pydantic import BaseModel

from .document_schemas import *

class ExceptionResponseSchema(BaseModel):
    error: str
