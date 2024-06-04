from enum import Enum


class ProductErrors(str, Enum):
    PRODUCT_NOT_FOUND: str = 'product not found'