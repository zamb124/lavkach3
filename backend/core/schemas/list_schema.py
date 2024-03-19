from typing import Any, Type

from pydantic import BaseModel, model_validator
from typing import Optional, List


class GenericListSchema(BaseModel):
    """
    example
    class CompanyListSchema(BaseListSchame):
    data: List[CompanyScheme] = []
    """
    size: int = 0
    cursor: int = 0
    prevcursor: int = 0
    data: Optional[List] = []


    @model_validator(mode='before')
    def mixin(cls: Type['Model'], data: Any) -> 'Model':
        if data['data']:
            cursor = max([i.lsn for i in data['data']])
            return {
                'size': len(data['data']),
                'data': data['data'],
                'cursor': cursor,
            }
        return data

    class Config:
        orm_mode = False
        arbitrary_types_allowed = True
        extra = 'allow'

