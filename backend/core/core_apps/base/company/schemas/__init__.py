from pydantic import BaseModel

from .company_schemas import CompanyCreateScheme, CompanyFilter, CompanyScheme, CompanyUpdateScheme, CompanyListSchema


class ExceptionResponseSchema(BaseModel):
    error: str
