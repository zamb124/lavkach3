from collections import defaultdict
from itertools import product
from uuid import UUID

from starlette.requests import Request

from app.front.apps.inventory.inventory import order
from app.inventory.location import Location, LocationType
from app.inventory.location.enums import PhysicalStoreLocationClass
from app.inventory.order.enums.order_enum import OrderClass
from app.inventory.schemas import Product
from core.core_apps.bus.bus.enums import LocationClass
from core.env import Model


class InventoryService:
    def __init__(self, request: Request):
        self.request = request
        self.env = request.scope['env']

    async def create_movements(self, schema):
        # Подбирает тип ордера и создает перемещения
        quant_model: Model = self.env['quant']
        order_type_model: Model = self.env['order_type']
        location_model: Model = self.env['location']
        location_src_ids: [UUID]   = []
        location_dest_ids: [UUID]  = []
        location_type_src: LocationType | None = None
        location_type_dest: LocationType | None = None
        # 1 - Сначала надо подобрать order_type_id, если его нет
        # 2 - Берем все типы ордеров, у которых класс internal
        order_types = await order_type_model.service.list({
            'order_class__in': [OrderClass.INTERNAL],
        })
        assert order_types, 'Не найдено ни одного типа ордера'
        if schema.location_src_id:
            location_src_ids  = await location_model.service.get_location_hierarchy(
                [schema.location_src_id, ]
            )
        if schema.location_type_src_id:
            location_type_src = await location_model.service.get(schema.location_type_src_id)
        if schema.location_dest_id:
            location_dest_ids = await location_model.service.get_location_hierarchy(
                [schema.location_dest_id, ]
            )
        if schema.location_type_dest_id:
            location_type_dest = await location_model.service.get(schema.location_type_dest_id)
        order_type_map: dict[str, dict[str, list]] = {}
        for order_type in order_types:
            order_type_map[order_type.id] = {
                'location_class_src_ids': list(
                    set(order_type.allowed_location_class_src_ids) -
                    set(order_type.exclude_location_class_src_ids)
                ),
                'location_type_src_ids':  list(
                    set(order_type.allowed_location_type_src_ids) -
                    set(order_type.exclude_location_type_src_ids)
                ),
                'location_src_ids':  list(
                    set(await location_model.service.get_location_hierarchy(
                    order_type.allowed_location_src_ids
                    )) -
                    set(order_type.exclude_location_src_ids)
                ),
                'location_class_dest_ids': list(
                    set(order_type.allowed_location_class_dest_ids) -
                    set(order_type.exclude_location_class_dest_ids)
                ),
                'location_type_dest_ids':  list(
                    set(order_type.allowed_location_type_dest_ids) -
                    set(order_type.exclude_location_type_dest_ids)
                ),
                'location_dest_ids': list(
                    set(await location_model.service.get_location_hierarchy(
                     order_type.allowed_location_dest_ids
                    )) -
                    set(order_type.exclude_location_dest_ids)
                ),
                'partner_id': order_type.partner_id,
                'store_id': order_type.store_id,
            }
        if not schema.products:
            available_src_quants = await quant_model.service.get_available_quants(
                store_id=schema.store_id,
                location_ids=location_src_ids,
                location_class_ids=[schema.location_class, ] if schema.location_class_src_id else list(
                    PhysicalStoreLocationClass),
                location_type_ids=[schema.location_type_src_id, ] if schema.location_type_src_id else None,
                partner_id=schema.partner_id if schema.partner_id else None,
                quantity=0.0
            )
            grouped_quants = defaultdict(lambda: {'quantity': 0, 'available_quantity': 0})

            for quant in available_src_quants:
                key = (quant.product_id, quant.lot_id, quant.partner_id)
                grouped_quants[key]['quantity'] += quant.quantity
                grouped_quants[key]['available_quantity'] += quant.available_quantity

            # Создаем модели Product на основе сгруппированных данных
            schema.products = [
                Product(
                    product_id=key[0],
                    lot_id=key[1],
                    quantity=data['quantity'],
                    avaliable_quantity=data['available_quantity']
                )
                for key, data in grouped_quants.items()
            ]
        else:
            for product in schema.products:
                    available_src_quants = await quant_model.service.get_available_quants(
                        product_id=product.product_id,
                        store_id=schema.store_id,
                        location_ids=location_src_ids,
                        location_class_ids=[schema.location_class,] if schema.location_class_src_id else list(
                            PhysicalStoreLocationClass),
                        location_type_ids=[schema.location_type_src_id,] if schema.location_type_src_id else None,
                        lot_ids=[product.lot_id] if product.lot_id else None,
                        partner_id=schema.partner_id if schema.partner_id else None,
                        quantity=0.0
                    )
                    product.available_quantity = sum([quant.available_quantity for quant in available_src_quants])
        a=1

