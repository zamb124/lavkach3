from datetime import datetime
from typing import List, Optional
import uuid
from pydantic import BaseModel, Field, HttpUrl, conint
from pydantic.types import UUID4, condecimal, constr
from app.to_camel import to_camel
from app.maintenance.models import Contractor
from core.repository.base import BaseRepo

class ContractorBaseScheme(BaseModel, BaseRepo):
    title: str = Field(description="Title")
    external_id: str = Field(description="External ID")
    company_id: UUID4
    class Config:
        model = Contractor
class ContractorUpdateScheme(ContractorBaseScheme):
    pass
class ContractorCreateScheme(ContractorBaseScheme):
    #lsn: condecimal = Field(description="Lsn")
    #id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    #title: str = Field(description="Title")
    #external_id: str = Field(description="External ID")
    class Config:
        model = Contractor
class ContractorScheme(ContractorCreateScheme):
    id: UUID4
    lsn: int

    class Config:
        model = Contractor
        orm_mode = True
        #alias_generator = to_camel
        #allow_population_by_field_name = True