from collections import defaultdict
from typing import Any

from starlette.requests import Request

from app.inventory.location import Location
from app.inventory.location.enums import PhysicalStoreLocationClass, PhysicalLocationClass
from app.inventory.order import MoveCreateScheme
from app.inventory.order.enums.exceptions_move_enums import MoveErrors
from app.inventory.order.enums.order_enum import OrderClass, MoveType
from app.inventory.quant import QuantScheme
from app.inventory.schemas import Product, Quant, Package
from core.env import Model
from core.exceptions.module import ModuleException


def compare_lists(list1, list2):
    # Проверка, что количество объектов в списках одинаковое
    if len(list1) != len(list2):
        return False

    # Сортировка списков по id объектов
    list1_sorted = sorted(list1, key=lambda x: x.id)
    list2_sorted = sorted(list2, key=lambda x: x.id)

    # Проверка, что объекты в списках идентичны
    for obj1, obj2 in zip(list1_sorted, list2_sorted):
        if obj1.quantity != obj2.quantity or obj1.available_quantity != obj2.available_quantity:
            return False

    return True


class InventoryService:
    def __init__(self, request: Request):
        self.request = request
        self.env = request.scope['env']

    async def create_movements(self, schema, commit=True):
        """
         Метод позволяет по разным параметрам создать перемещение товаров
        """
        quant_model: Model = self.env['quant']
        order_type_model: Model = self.env['order_type']
        location_model: Model = self.env['location']
        move_model: Model = self.env['move']
        location_src_ids: list[Location] = []
        # 1 - Сначала надо подобрать order_type_id, если его нет
        # 2 - Берем все типы ордеров, у которых класс internal
        order_types = await order_type_model.service.list({
            'order_class__in': [OrderClass.INTERNAL],
        })
        assert any([schema.location_src_zone_id, schema.location_src_id, schema.location_type_src_id, schema.products,
                    schema.packages]), 'Должно быть заполнено чет одно'
        assert order_types, 'Не найдено ни одного типа ордера'
        if schema.location_src_id:
            # Если указана локация, то достаем ее, а на зону уже не обращаем внимание
            location_src_ids = [await location_model.service.get(schema.location_src_id), ]
        elif schema.location_src_zone_id:
            # Если указана зона, достаем ее дочерние подзоны так же, что бы найти все физические зоны
            location_src_ids = await location_model.service.get_location_hierarchy(
                location_ids=[schema.location_src_zone_id],
                location_type_ids=[schema.location_type_src_id],
            )
        for loc in location_src_ids:
            # Если указана локация НЕ физическая зона, то выдаем ошибку
            if loc.location_class not in list(PhysicalLocationClass):
                raise ModuleException(
                    status_code=406, enum=MoveErrors.SOURCE_LOCATION_ERROR,
                    message='The source location must be Physical a zone',
                    args={'location_id': loc.id}
                )

        available_src_quants = await quant_model.service.get_available_quants(
            store_id=schema.store_id,
            location_ids={i.id for i in location_src_ids},
            product_ids={i.product_id for i in schema.products} if schema.products else None,
            package_ids={i.package_id for i in schema.packages} if schema.packages else None,
            partner_id=schema.partner_id if schema.partner_id else None,
            location_classes=list(PhysicalStoreLocationClass),
            lot_ids={i.lot_id for i in schema.products} if schema.products else None,
        )
        if not available_src_quants:
            raise ModuleException(
                status_code=406, enum=MoveErrors.SOURCE_LOCATION_ERROR,
                message='No available quants found in the source location'
            )
        grouped_quants: defaultdict[Any, dict[str, float | list]] = defaultdict(
            lambda: {'quantity': 0.0, 'available_quantity': 0.0, 'quants': []}
        )

        packages = defaultdict(list)
        for q in available_src_quants:
            if q.package_id:
                packages[q.package_id].append(q)

        for pack in packages:
            # Сравниваем найденные кванты и берем упаковки из бд, если они идентичны, считаем, что все в этих package_id
            # Перемещаем как Упаковки
            pack_quants = await quant_model.service.list({'package_id__in': [pack]})
            identical = compare_lists(pack_quants, packages[pack])
            if identical:
                # Удаляем из доступных для отбора квантов
                available_src_quants = [item for item in available_src_quants if item not in pack_quants]
                package = None
                for p in schema.packages:
                    if p.package_id == pack:
                        p.quants = [Quant.model_validate(q) for q in pack_quants]
                        package = p
                        break
                if package:
                    continue
                schema.packages.append(Package(
                    package_id=pack,
                    quants=[Quant.model_validate(q) for q in pack_quants]
                ))



        for quant in available_src_quants:
            if not quant.available_quantity > 0:
                continue
            key = (quant.product_id, quant.lot_id, quant.uom_id)
            grouped_quants[key]['quantity'] += quant.quantity
            grouped_quants[key]['available_quantity'] += quant.available_quantity
            grouped_quants[key]['quants'].append(quant)
            if quant.package_id:
                packages[quant.package_id].append(quant)

        # Создаем модели Product на основе сгруппированных данных
        if not schema.products:
            schema.products = [
                Product(
                    product_id=key[0],
                    lot_id=key[1],
                    uom_id=key[2],
                    quantity=data['available_quantity'],
                    avaliable_quantity=data['available_quantity'],
                    quants=[Quant.model_validate(q) for q in data['quants']]  # type: ignore
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
                product.quants = [Quant.model_validate(q) for q in grouped_q['quants']]

        # Подбираем тип ордера
        product_order_types_map = await order_type_model.service.get_appropriate_order_types(
            products=[(i.product_id, q.location_id) for i in schema.products for q in i.quants],
            zone_dest_id=schema.location_dest_zone_id,
            location_dest_id=schema.location_dest_id
        )
        packade_order_type_map = await order_type_model.service.get_appropriate_order_types_for_packages(
            packages=[(i.package_id, q.location_id) for i in schema.packages for q in i.quants if i.quants],
            zone_dest_id=schema.location_dest_zone_id,
            location_dest_id=schema.location_dest_id
        )
        # Итерируемся по Каждому товару--> Каждому кванту и подбираем тип ордера для каждого
        for prod in schema.products:
            to_move = 0.0
            to_moves_qty = min(prod.quantity, prod.avaliable_quantity)  # Сколько надо переместить
            if to_moves_qty <= 0:
                continue
            for q in prod.quants:
                # Подбираем ORDER_TYPE
                # Подбираем количество из каждого кванта
                if to_moves_qty <= 0:
                    break
                if to_moves_qty <= q.available_quantity:
                    to_move = to_moves_qty
                    to_moves_qty = 0.0
                elif to_moves_qty > q.available_quantity:
                    to_move = q.available_quantity
                    to_moves_qty -= q.available_quantity
                q.qty_to_move = to_move
                q.location_dest_id = schema.location_dest_id
        # находим цельные упаковки, группируем кванты по package_id
        for product in schema.products:
            for q in product.quants:
                prod_allowed_order_types = product_order_types_map.get(product.product_id)
                move_obj = MoveCreateScheme(
                    type=MoveType.PRODUCT,
                    store_id=q.store_id,
                    location_src_id=q.location_id,
                    quant_src_id=q.id,
                    order_type_id=prod_allowed_order_types[0].id,
                    location_dest_id=schema.location_dest_id,
                    product_id=q.product_id,
                    quantity=q.quantity,
                    uom_id=q.uom_id,
                    lot_id=q.lot_id,
                )

                product.moves.append(move_obj)
        for pack in schema.packages:
            order_types = packade_order_type_map.get(pack.package_id)
            quant = None
            for q in pack.quants:
                q.qty_to_move = 1
                q.location_dest_id = schema.location_dest_id
                quant = q
            move_obj = MoveCreateScheme(
                type=MoveType.PACKAGE,
                store_id=schema.store_id,
                location_src_id=quant.location_id,
                quantity=1,
                order_type_id=order_types[0].id,
                location_dest_id=schema.location_dest_id,
            )
            pack.moves.append(move_obj)
        if commit:
            ...
        return schema
