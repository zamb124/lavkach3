from datetime import datetime
from typing import Optional, List, Any

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic.types import UUID4
from app.basic.product.models.product_models import Product, ProductType
from core.schemas import BaseFilter
from core.schemas.list_schema import GenericListSchema
from core.schemas.timestamps import TimeStampScheme
from app.basic.company.schemas import CompanyScheme
from app.basic.uom.schemas import UomScheme


class ProductBaseScheme(BaseModel):
    vars: Optional[dict] = None
    title: str = Field(title='Title', table=True, form=True)
    description: Optional[str] = Field(default=None, title='Description', table=True, form=True)
    external_number: Optional[str] = Field(default=None, title='External #', table=True, form=True)
    product_type: ProductType = Field(default=ProductType.STORABLE, title='Type', table=True, form=True)
    uom_id: UUID4 = Field(title='Uom', table=True, form=True)
    product_category_id: UUID4 = Field(title='Product Category', table=True, form=True)
    product_storage_type_id: UUID4 = Field(title='Product Storage type', table=True, form=True)
    barcode_list: list[str] = Field(default=None, title='Barcodes', table=True, form=True)

    class Config:
        extra = 'allow'
        from_attributes = True
        orm_model = Product
        service = 'app.basic.product.services.ProductService'

    @model_validator(mode='before')
    @classmethod
    def check_card_number_omitted(cls, data: Any) -> Any:
        if isinstance(data, dict):
            barcode_list_str = data.get('barcode_list')
            if barcode_list_str and isinstance(barcode_list_str, str):
                try:
                    barcode_list = barcode_list_str.split(',')
                    data['barcode_list'] = barcode_list
                except Exception as ex:
                    pass
        return data

class ProductUpdateScheme(ProductBaseScheme):
    ...


class ProductCreateScheme(ProductBaseScheme):
    ...


class ProductScheme(ProductCreateScheme, TimeStampScheme):
    lsn: int
    id: UUID4
    uom_rel: UomScheme
    company_id: UUID4

    class Config:
        from_attributes = True


class ProductFilter(BaseFilter):
    title__in: Optional[List[str]] = Field(description="title", default=None)

    class Config:
        populate_by_name = True

    class Constants(Filter.Constants):
        model = Product
        ordering_field_name = "order_by"
        search_field_name = "search"
        search_model_fields = ["title", "external_number"]


class ProductListSchema(GenericListSchema):
    data: Optional[List[ProductScheme]]
