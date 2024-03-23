from datetime import datetime, timedelta
from typing import Optional

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import BaseModel, Field, UUID4, model_validator, field_validator
from typing import Optional, List, TYPE_CHECKING, Any

from pydantic_core import PydanticCustomError

created_at_gte_default = datetime.now() - timedelta(days=365)
created_at_lt_default = datetime.now() + timedelta(days=365)


class BaseFilter(Filter):
    """
        Аттрибут filter=True - значит будет показываться в UI на фильтрах
        Можно переопределить дальше эту схему уже в BFF
    """
    search: Optional[str] = Field(default=None, filter=True, title='Search')
    lsn__gt: Optional[int] = Field(alias="cursor", default=0)
    id__in: Optional[List[UUID4]] = Field(alias="id", default=None, title='ID')
    created_at__gte: Optional[datetime] = Field(description="bigger or equal created", default=None, filter=True, title='Created at from')
    created_at__lt: Optional[datetime] = Field(description="less created", default=None, filter=True, title='Created at to')
    updated_at__gte: Optional[datetime] = Field(description="bigger or equal updated", default=None, filter=True, title='Updated at from')
    updated_at__lt: Optional[datetime] = Field(description="less updated", default=None, filter=True, title='Created at to')
    company_id__in: Optional[List[UUID4]] = Field(alias="company_id", default=None, title='Company')
    order_by: Optional[List[str]] = Field(default=["lsn", ], filter=True, title='Order by')

    @model_validator(mode='before')
    def check(cls, value):
        """
            Так же убираем все пустые params
        """

        to_del = []
        for k, v in value.items():
            if not v:
                to_del.append(k)
        for i in to_del:
            value.pop(i)
        return value


    class Config:
        populate_by_name = True

    class Constants(Filter.Constants):
        ordering_field_name = "order_by"
        search_field_name = "search"