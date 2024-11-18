from typing import Any, Type
from typing import Optional, List

from pydantic import BaseModel, model_validator


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
            if not getattr(data['data'][0], 'lsn'):
                cursor = 99999
            else:
                cursor = max([i.lsn for i in data['data']])
            return {
                'size': len(data['data']),
                'data': data['data'],
                'cursor': cursor,
            }
        return data

    class Config:
        from_attributes = False
        arbitrary_types_allowed = True
        extra = 'allow'

