from datetime import datetime, timedelta
from typing import Optional, List, Iterable

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import BaseModel, Field, UUID4, model_validator

created_at_gte_default = datetime.now() - timedelta(days=365)
created_at_lt_default = datetime.now() + timedelta(days=365)




class BaseFilter(Filter):
    """
        Аттрибут filter=True - значит будет показываться в UI на фильтрах
        Можно переопределить дальше эту схему уже в BFF
    """
    search: Optional[str] = Field(default='',  title='Search')
    lsn__gt: Optional[int] = Field(alias="cursor", title='Lsn', default=0)
    id__in: Optional[List[UUID4]] = Field(default=None, title='ID')
    created_at__gte: Optional[datetime] = Field(default=None,  title='Created at from')
    created_at__lt: Optional[datetime] = Field(default=None,  title='Created at to')
    updated_at__gte: Optional[datetime] = Field(default=None,  title='Updated at from')
    updated_at__lt: Optional[datetime] = Field(default=None,  title='Updated at to')
    #company_id__in: Optional[List[UUID4]] = Field(alias="company_id", default=None, title='Company')
    order_by: Optional[List[str]] = Field(default=["lsn", ], title='Order by')


    @model_validator(mode='before')
    def check(cls, value):
        """
            Так же убираем все пустые params
        """

        to_del = []
        for k, v in value.items():
            if _id := value.get('id__in'):
                if not isinstance(_id, Iterable):
                    value['id__in'] = [_id,]
            if not v:
                to_del.append(k)
        for i in to_del:
            value.pop(i)
        return value


    class Config:
        populate_by_name = True
        extra = 'allow'

    class Constants(Filter.Constants):
        ordering_field_name = "order_by"
        search_field_name = "search"


    def as_params(self):
        params = {}
        dump = self.model_dump(mode='json')
        for field in self.model_fields_set:
            f = dump.get(field)
            if isinstance(f, Iterable):
                params.update({field: ','.join(f)})
            else:
                params.update({field: f})
        return params
class CustomBaseModel(BaseModel):

    def ui_sort(self):
        return self
