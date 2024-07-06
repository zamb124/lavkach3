from .document_schemas import *

class ExceptionResponseSchema(BaseModel):
    error: str
