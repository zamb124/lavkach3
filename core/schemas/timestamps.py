import uuid

from pydantic import BaseModel, Field, UUID4
from datetime import datetime
#from core.service.base import BaseRepo
from app.company.models import Company
from typing import Optional


class TimeStampScheme(BaseModel):
    created_at: datetime
    updated_at: datetime