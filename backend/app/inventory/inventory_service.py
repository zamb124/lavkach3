from collections import defaultdict
from typing import Any, Optional
from uuid import UUID

from starlette.requests import Request

from app.inventory.location import Location
from app.inventory.location.enums import PhysicalStoreLocationClass
from app.inventory.order import OrderType
from app.inventory.order.enums.exceptions_move_enums import MoveErrors
from app.inventory.order.enums.order_enum import OrderClass
from app.inventory.product_storage import ProductStorageType
from app.inventory.schemas import Product, Quant
from core.env import Model
from core.exceptions.module import ModuleException


def get_intersection(list1, list2):
    return list(set(list1) & set(list2))

class InventoryService:
    def __init__(self, request: Request):
        self.request = request
        self.env = request.scope['env']

    async def create_movements(self, schema):
        # Подбирает тип ордера и создает перемещения
        quant_model: Model = self.env['quant']
        order_type_model: Model = self.env['order_type']
        location_model: Model = self.env['location']
        product_storage_type: Model = self.env['product_storage_type']
        location_src_ids: list[Location]   = []
        # 1 - Сначала надо подобрать order_type_id, если его нет
        # 2 - Берем все типы ордеров, у которых класс internal
        order_types = await order_type_model.service.list({
            'order_class__in': [OrderClass.INTERNAL],
        })
        #assert not (schema.products and schema.packages), 'Должно быть заполнено или schema.products, или schema.packages, или ничего из них'
        assert any([schema.location_src_id, schema.location_type_src_id, schema.products, schema.packages]), 'Должно быть заполнено чет одно'
        assert order_types, 'Не найдено ни одного типа ордера'
        if schema.location_src_id:
            location_src_ids = await location_model.service.get_location_hierarchy(
                location_ids=[schema.location_src_id],
                location_type_ids=[schema.location_type_src_id],
            )

        available_src_quants = await quant_model.service.get_available_quants(
            store_id=schema.store_id,
            location_ids={i.id for i in location_src_ids},
            product_ids={i.product_id for i in schema.products} if schema.products else None,
            package_ids={i.package_id for i in schema.packages} if schema.packages else None,
            partner_id=schema.partner_id if schema.partner_id else None,
            location_classes=list(PhysicalStoreLocationClass),
            lot_ids={i.lot_id for i in schema.products} if schema.products else None,
            quantity=0.0
        )
        grouped_quants: defaultdict[Any, dict[str, float | list]] = defaultdict(lambda: {'quantity': 0.0, 'available_quantity': 0.0, 'quants': []})
        for quant in available_src_quants:
            if not quant.available_quantity > 0:
                continue
            key = (quant.product_id,  quant.lot_id, quant.uom_id)
            grouped_quants[key]['quantity'] += quant.quantity
            grouped_quants[key]['available_quantity'] += quant.available_quantity
            grouped_quants[key]['quants'].append({  # type: ignore
                'quant_id': quant.id,
                'package_id': quant.package_id,
                'location_src_id': quant.location_id,
                'quantity': quant.available_quantity
            })
        # Создаем модели Product на основе сгруппированных данных
        if not schema.products:
            schema.products = [
                Product(
                    product_id=key[0],
                    lot_id=key[1],
                    uom_id=key[2],
                    quantity=data['available_quantity'],
                    avaliable_quantity=data['available_quantity'],
                    quants=[Quant(**q) for q in data['quants']]  # type: ignore
                )
                for key, data in grouped_quants.items()
            ]
        else:
            # Делаем из Product ключ, что бы найти подходящие по ключу кванты
            products_dict_map = {
                (product.product_id, product.lot_id, product.uom_id): product
                for product in schema.products
            }
            for key, product in products_dict_map.items():
                grouped_q = grouped_quants.get(key)
                if not grouped_q:
                    product.avaliable_quantity = 0.0
                    continue
                product.avaliable_quantity = grouped_q['available_quantity']
                product.quants = [Quant(**q) for q in grouped_q['quants']]  # type: ignore
        # Далее нам нужно проверить, если мы берем всю упаковку, а не конкретные товары и упаковок,
        # ТК если всю, то как будето логично взять всю упаковку

        # Подбираем тип ордера
        # Достаем все Зоны тех локаций, которые подобраны в квантах
        quant_location_ids = {i.location_src_id for i in schema.products for i in i.quants}
        # Собираем всех родителей тех локаций, к которым прикреплены кванты
        # Что бы найти все ZONE этих локаций
        parents_location_src_map = await location_model.service.get_all_parent_zones(location_ids=quant_location_ids)
        parents_location_dest_map: dict[str, list] = {}
        if schema.location_dest_id:
            parents_location_dest_map = await location_model.service.get_all_parent_zones(
                location_ids=[schema.location_dest_id]
            )
        # Берем все продукты, что бы найти их стратегии приемки
        product_storage_types = await product_storage_type.service.get_storage_types_by_products(
            product_ids={i.product_id for i in schema.products}
        )
        product_storage_type_map: dict[UUID, ProductStorageType] = {
            i.product_id: i for i in product_storage_types
        }
        # Собираем все возможные типы ордеров для каждой зоны
        src_zones_order_type = defaultdict(list)
        for order_type in order_types:
            for src_zone_id in order_type.allowed_zone_src_ids:
                src_zones_order_type[src_zone_id].append(order_type)

        # Итерируемся по Каждому товару--> Каждому кванту и подбираем тип ордера для каждого
        for prod in schema.products:
            to_move = 0.0
            to_moves_qty = min(prod.quantity, prod.avaliable_quantity)  # Сколько надо переместить

            # Берем для товара его стратегию приемки и вычленяем зоны, куда можно его перемещать
            parent_zones_dest_q = [
                UUID(v) for k, v in product_storage_type_map.get(prod.product_id).  # type: ignore
                storage_type_rel.allowed_zones.items()
                if k == 'zone_id'
            ]
            if schema.location_dest_id:
                # Если указана Зона или ячейка куда перемещаем, то убеждаемся, что товар можно туда перемешать
                parent_zones_dest_q = get_intersection(
                    parent_zones_dest_q, parents_location_dest_map.get(schema.location_dest_id)
                )
                if not parent_zones_dest_q:
                    raise ModuleException(
                        status_code=406, enum=MoveErrors.DESTINATION_LOCATION_ERROR,
                        message='The {product} cannot be moved to the specified {area}',
                        args={'product_id': prod.product_id, 'location_id': schema.location_dest_id}
                    )
            if to_moves_qty <= 0:
                continue
            for q in prod.quants:
                # Подбираем ORDER_TYPE
                parent_zones_src_q = parents_location_src_map.get(q.location_src_id)
                move_order_type: Optional[OrderType] = None
                for zone_id in parent_zones_src_q:
                    if zone_id in src_zones_order_type:
                        order_types = src_zones_order_type[zone_id]
                        for order_type in order_types:
                            if any([i in parent_zones_dest_q for i in order_type.allowed_zone_dest_ids]):
                                move_order_type = order_type
                                break
                if not move_order_type:
                    raise ModuleException(status_code=406, enum=MoveErrors.DESTINATION_LOCATION_ERROR, message='Не найден тип ордера для перемещения')

                # Подбираем количество из каждого кванта
                if to_moves_qty <= 0:
                    break
                if to_moves_qty <= q.quantity:
                    to_move = to_moves_qty
                    to_moves_qty = 0.0
                elif to_moves_qty > q.quantity:
                    to_move = q.quantity
                    to_moves_qty -= q.quantity
                q.quantity = to_move
                q.order_type_id = move_order_type.id
        return schema
