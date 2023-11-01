from typing import Any, Type

from pydantic import BaseModel
from typing import Optional, List

class GenericListSchema(BaseModel):
    size: Optional[int]
    cursor: Optional[int]

    @classmethod
    def validate(cls: Type['Model'], value: Any) -> 'Model':
        if value and value.get('data') and value:
            cursor = max([i.lsn for i in value['data']])
            value.update({
                'cursor': cursor
            })
        return super(GenericListSchema, cls).validate(value)

class BaseListSchame(BaseModel):
    """
    example
    class CompanyListSchema(BaseListSchame):
    data: List[CompanyScheme] = []
    """
    cursor: int = 0
    data: List = []
    len: int = 0

    @classmethod
    def validate(cls: Type['Model'], value: Any) -> 'Model':
        if value:
            for i in value:
                if isinstance(i, dict):
                    cursor = max([i['lsn'] for i in value])
                else:
                    cursor = max([i.lsn for i in value])
            value = {
                'data': value,
                'cursor': cursor,
                'len': len(value),
            }
        return super(BaseListSchame, cls).validate(value)

    class Config:
        orm_mode = False
        arbitrary_types_allowed = True

