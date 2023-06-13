from .contractor import *
from .service_supplier import *
from .manufacturer import *
from .model import *
from .asset_type import *
from .asset import *
from .asset_log import *
from .order import *


class ExceptionResponseSchema(BaseModel):
    error: str
