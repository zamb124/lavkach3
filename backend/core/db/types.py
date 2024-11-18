import uuid
from typing import Annotated

from sqlalchemy import Uuid, ARRAY
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import mapped_column


# from app.inventory.location.models import Location, LocationClass
class UniqueList(MutableList):
    def append(self, value):
        if value not in self:
            super().append(value)
            self.changed()

    def extend(self, values):
        for value in values:
            if value not in self:
                super().append(value)
        self.changed()

    def insert(self, index, value):
        if value not in self:
            super().insert(index, value)
            self.changed()


ids = Annotated[list[uuid.UUID], mapped_column(UniqueList.as_mutable(ARRAY(Uuid)), server_default='{}', nullable=False)]
