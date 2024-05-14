from pydantic import BaseModel, UUID4

from app.inventory.order.models import SuggestType  # todo: зависимость от чужого сервиса


#
# class Suggest(BaseModel):
#     public_id: UUID4
#     public_order_id: UUID4
#     public_shelf_id: UUID4
#     public_product_id: UUID4
#     status: str # enum
#     count: float
    # conditions: ConditionSuggest # todo; нужно ли?
    #
    # title: str = Field(description="Title")
    # external_id: Optional[str] = None
    # locale: Optional[TypeLocale] = None
    # country: Optional[TypeCountry] = None
class Suggest(BaseModel):
    public_id: UUID4
    public_move_id: UUID4
    type: SuggestType
    count: float
    # value: float
    user_done_id: UUID4
