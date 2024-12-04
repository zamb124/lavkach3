from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy import select
from starlette.exceptions import HTTPException
from starlette.requests import Request

from app.basic.uom.models.uom_models import Uom
from app.basic.uom.schemas.uom_schemas import UomCreateScheme, UomUpdateScheme, UomFilter, ConvertSchema
from core.service.base import BaseService
from decimal import Decimal, ROUND_HALF_UP

from core.utils.uom import calculate_quantity


class UomService(BaseService[Uom, UomCreateScheme, UomUpdateScheme, UomFilter]):
    def __init__(self, request: Request):
        super(UomService, self).__init__(request, Uom, UomCreateScheme, UomUpdateScheme)



    async def convert(self, obj: ConvertSchema):
        uom_in = await self.session.execute(select(Uom).where(Uom.id == obj.uom_id_in))
        uom_in = uom_in.scalar_one_or_none()
        if not uom_in:
            raise HTTPException(status_code=404, detail=f"UOM with id {obj.uom_id_in} not found")

        if obj.uom_id_out:
            uom_out = await self.session.execute(select(Uom).where(Uom.id == obj.uom_id_out))
            uom_out = uom_out.scalar_one_or_none()
            if not uom_out:
                raise HTTPException(status_code=404, detail=f"UOM with id {obj.uom_id_out} not found")
        else:
            uom_out = await self.session.execute(
                select(Uom).where(Uom.type == 'standart', Uom.uom_category_id == uom_in.uom_category_id))
            uom_out = uom_out.scalar_one_or_none()
            if not uom_out:
                raise HTTPException(status_code=404, detail="Standard UOM not found in the same category")

        if uom_in.uom_category_id != uom_out.uom_category_id:
            raise HTTPException(status_code=400, detail="Cannot convert between different UOM categories")

          # Преобразование quantity_in в Decimal

        quantity_out = calculate_quantity(
            uom_in.type, uom_in.ratio, uom_out.type,
            uom_out.ratio, uom_out.precision, obj.quantity_in
        )

        return {
            'uom_id_in': obj.uom_id_in,
            'uom_ratio_in': uom_in.ratio,
            'uom_precision_in': uom_in.precision,
            'quantity_in': obj.quantity_in,
            'uom_id_out': obj.uom_id_out,
            'uom_ratio_out': uom_out.ratio,
            'uom_precision_out': uom_out.precision,
            'quantity_out': quantity_out
        }
