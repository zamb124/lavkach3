import datetime

import pytest

from app.inventory.location.enums import PutawayStrategy
from app.inventory.order.models import OrderClass, BackOrderAction, ReservationMethod
from tests.conftest import *

@pytest.mark.asyncio
async def test_crud_order_type(async_inventory_client, headers, stores, companies, products, locations, token):
    """
    Проверяем rруд вокруг товаров
    """
    create_data = {
        'company_id': companies[0].id.__str__(),
        'prefix': 'IN',
        'title': 'title',
        'order_class': 'incoming',
        'allowed_location_src_ids': [locations['partner'].id.__str__(),],
        'exclusive_location_src_ids': None,
        'allowed_location_dest_ids': [locations['place'].id.__str__(),],
        'exclusive_location_dest_ids': None,
        'backorder_order_type_id': None,
        'backorder_action_type': 'ask',
        'store_id': None,
        'partner_id': None,
        'reservation_method': 'at_confirm',
        'reservation_time_before': 0,
        'allowed_package_ids': [locations['package'].id.__str__(),],
        'exclusive_package_ids': None,
        'homogeneity': False,
        'allow_create_package': True,
        'can_create_order_manualy': True,
        'overdelivery': False,
        'created_by': token['user_admin']['user_id'].__str__(),
        'edited_by': token['user_admin']['user_id'].__str__(),
        'barcode': '2132132131231',
        'strategy': 'fefo',
    }
    response = await async_inventory_client.post("/api/inventory/order_type/create", json=create_data, headers=headers['superadmin'])
    assert response.status_code == 200
    data = response.json()
    order_type_id_1 = data['id']
    #--------------------------------
    # Изменяем
    update_data = {
        'expiration_date': datetime.datetime.now().isoformat(),
        'product_id': products[0].id.__str__(),
        'external_id': '1000002',
    }
    response = await async_inventory_client.put(f"/api/inventory/lot/{lot_id_1}", json=update_data, headers=headers['superadmin'], )
    assert response.status_code == 200
    # --------------------------------
    # Поиск
    response = await async_inventory_client.get("/api/inventory/lot", headers=headers['superadmin'], params={'size': 100, 'search': '1000002'}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data.get('data')) == 1
    # Удаление
    response = await async_inventory_client.delete(f"/api/inventory/lot/{lot_id_1}", headers=headers['superadmin'], )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_crud_quant(async_inventory_client, headers, stores, companies, products, lots, uoms, locations):
    """
    Проверяем rруд вокруг товаров
    """
    create_data = {
        'company_id': companies[0].id.__str__(),
        'product_id': products[0].id.__str__(),
        'store_id': stores[0].id.__str__(),
        'location_id': locations['place'].id.__str__(),
        'lot_id': lots[0].id.__str__(),
        'quantity': 10.0,
        'reserved_quantity': 5,
        'expiration_date': datetime.datetime.now().isoformat(),
        'uom_id': uoms[0].id.__str__()
    }
    response = await async_inventory_client.post("/api/inventory/quant/create", json=create_data, headers=headers['superadmin'])
    assert response.status_code == 200
    data = response.json()
    lot_id_1 = data['id']
    #--------------------------------
    # Изменяем
    update_data = {
        'product_id': products[0].id.__str__(),
        'store_id': stores[1].id.__str__(),
        'location_id': locations['zone'].id.__str__(),
        'lot_id': None,
        'quantity': 2.5,
        'reserved_quantity': 8,
        'expiration_date': datetime.datetime.now().isoformat(),
        'uom_id': uoms[1].id.__str__()
    }
    response = await async_inventory_client.put(f"/api/inventory/quant/{lot_id_1}", json=update_data, headers=headers['superadmin'], )
    assert response.status_code == 200
    # --------------------------------
    # Поиск
    response = await async_inventory_client.get("/api/inventory/quant", headers=headers['superadmin'], params={'size': 100, 'search': '1000002'}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data.get('data')) == 1
    # Удаление
    response = await async_inventory_client.delete(f"/api/inventory/quant/{lot_id_1}", headers=headers['superadmin'], )
    assert response.status_code == 200