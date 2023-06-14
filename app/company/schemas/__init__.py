from .company_schemas import *


class ExceptionResponseSchema(BaseModel):
    error: str
