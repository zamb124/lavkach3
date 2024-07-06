from sqlalchemy import select
from starlette.requests import Request

from app.basic.uom.models.uom_models import Uom
from app.basic.uom.schemas.uom_schemas import UomCreateScheme, UomUpdateScheme, UomFilter, ConvertSchema
from core.service.base import BaseService


class UomService(BaseService[Uom, UomCreateScheme, UomUpdateScheme, UomFilter]):
    def __init__(self, request: Request):
        super(UomService, self).__init__(request, Uom, UomCreateScheme, UomUpdateScheme)

    async def convert(self, objs: list[ConvertSchema]):
        ids = []
        for o in objs:
            ids.append(o.uom_id_in)
            ids.append(o.uom_id_out)
        query = select(self.model).filter(self.model.id.in_(ids))
        result = self.session.execute(query)
        result = {i.id: i for i in result}
        # for obj in objs:
        #
        # uom_id_in_entity = await self.get(obj)
        # uom_id_out_entity = await self.get(uom_id_out)
        #
        # await self.session.delete(entity)
        # try:
        #     await self.session.commit()
        # except IntegrityError as e:
        #     await self.session.rollback()
        #     if "duplicate key" in str(e):
        #         raise HTTPException(status_code=409, detail=f"Conflict Error entity {str(e)}")
        #     else:
        #         raise HTTPException(status_code=500, detail=f"ERROR:  {str(e)}")
        # except Exception as e:
        #     raise HTTPException(status_code=500, detail=f"ERROR:  {str(e)}")
        return True
