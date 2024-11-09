import uuid
from typing import Annotated

from sqlalchemy import Uuid, ARRAY
from sqlalchemy.ext.mutable import MutableList, MutableSet
from sqlalchemy.orm import mapped_column

# from app.inventory.location.models import Location, LocationClass

ids = Annotated[list[uuid.UUID], mapped_column(MutableList.as_mutable(ARRAY(Uuid)), server_default='{}', nullable=False)]

