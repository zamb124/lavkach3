import enum
import uuid
from enum import Enum
from typing import Optional, Annotated
import datetime
from sqlalchemy import Column, Unicode, Sequence, Uuid, ForeignKey, DateTime, func, text, UniqueConstraint, ARRAY, \
    String, JSON
from sqlalchemy.orm import relationship, mapped_column, Mapped

from app.inventory.location.models import Location
from core.db import Base
from core.db.mixins import AllMixin, guid, guid_primary_key
from app.inventory.quant.models import Lot, Quant
# from app.inventory.location.models import Location, LocationClass
from app.inventory.location.enums import LocationClass, PutawayStrategy

ids = Annotated[list[uuid.UUID], mapped_column(ARRAY(Uuid), default=[], nullable=False)]
enum_ids = Annotated[list, mapped_column(type_=ARRAY(String))]
