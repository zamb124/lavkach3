from datetime import datetime
from typing import Optional

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import BaseModel, Field, UUID4, model_validator
from typing import Optional, List, TYPE_CHECKING, Any
class BaseFilter(Filter):
    lsn__gt: Optional[int] = Field(alias="cursor", default=0)
    id__in: Optional[List[UUID4]] = Field(alias="id", default=None)
    created_at__gte: Optional[datetime] = Field(description="bigger or equal created", default=None)
    created_at__lt: Optional[datetime] = Field(description="less created", default=None)
    updated_at__gte: Optional[datetime] = Field(description="bigger or equal updated", default=None)
    updated_at__lt: Optional[datetime] = Field(description="less updated", default=None)
    company_id__in: Optional[List[UUID4]] = Field(alias="company_id", default=None)
    order_by: Optional[List[str]] = ["created_at"]
    search: Optional[str] = None

    @model_validator(mode="before")
    def check_root_validator(cls, value):
        """
            сериализует дейтрендж
            Так же убираем все пустые params
        """
        to_del = []
        for k,v in value.items():
            if not v:
                to_del.append(k)
        if value.get('date_planned_range'):
            gte, lt = value['date_planned_range'].split(':')
            value.update({
                'planned_date__gte': datetime.fromisoformat(gte),
                'planned_date__lt': datetime.fromisoformat(f'{lt}T23:59:59')
            })
            value.pop('date_planned_range')
        for i in to_del:
            value.pop(i)
        return value

    class Config:
        populate_by_name = True

    class Constants(Filter.Constants):
        ordering_field_name = "order_by"
        search_field_name = "search"