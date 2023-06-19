from pydantic import BaseModel, Field
from pydantic.types import UUID4

from backend.app.maintenance.schemas.contractor_schemas import ContractorScheme
from backend.core.schemas.timestamps import TimeStampScheme


class ServiceSupplierBaseScheme(BaseModel):
    title: str = Field(description="Title")
    external_id: str = Field(description="External ID")
    contractor_id: UUID4
class ServiceSupplierUpdateScheme(ServiceSupplierBaseScheme):
    pass
class ServiceSupplierCreateScheme(ServiceSupplierBaseScheme):
    pass
class ServiceSupplierScheme(ServiceSupplierCreateScheme, TimeStampScheme):
    id: UUID4
    lsn: int
    contractor: ContractorScheme
    class Config:
        orm_mode = True