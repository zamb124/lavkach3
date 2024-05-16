from core.fastapi.adapters import BaseAdapter


class TerminalAdapter(BaseAdapter):
    module = 'inventory'

    async def order(self, params=None, **kwargs):
        # responce = await self.session.get(self.domain + path, params=params)
        # data = responce.json()



        return [
        {
            "number": "PO-001",
            "order_type": "acceptance",
            "parent_id": None,
            "external_number": "EXT-001",
            "partner_id": "5b0f6c8b-04c5-4a9c-ae8d-3d0b8e1b9ec6",
            "planned_date": "2023-01-01T00:00:00"
        },
        {
            "number": "PO-002",
            "order_type": "acceptance",
            "parent_id": None,
            "external_number": None,
            "partner_id": "5b0f6c8b-04c5-4a9c-ae8d-3d0b8e1b9ec8",  # нужно доставать по умолчанию name объекта, схема запроса != схеме в бд!
            "planned_date": "2023-01-02T00:00:00"
        }
    ]

