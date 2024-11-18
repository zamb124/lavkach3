from datetime import datetime

from pydantic import BaseModel, Field


class TimeStampScheme(BaseModel):
    created_at: datetime = Field(title='Created at', table=False, description='Creation date, When the object was created')
    updated_at: datetime = Field(title='Updated at', table=False, description='Update date, When the object was updated last time')
