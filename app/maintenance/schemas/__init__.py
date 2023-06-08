from .contractor import *
from .service_supplier import *
from .manufacturer import *
from .model import *


class ExceptionResponseSchema(BaseModel):
    error: str
