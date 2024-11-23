import datetime
import random

import pytest
from sqlalchemy.orm.sync import update


@pytest.mark.asyncio
async def test_crud_lot(inventory_client, headers, stores, companies, products):
    """
    Проверяем rруд вокруг лота
    """
    create_data = {
        'company_id': companies[0].id.__str__(),
        'expiration_datetime': datetime.datetime.now().isoformat(),
        'product_id': products[0].id.__str__(),
        'external_number': str(random.randint(100000, 888888)),
        # 'partner_id': 'partner'
    }
    response = await inventory_client.post("/api/inventory/lot", json=create_data, headers=headers['superadmin'])
    assert response.status_code == 200
    data = response.json()
    lot_id_1 = data['id']
    # --------------------------------
    # Изменяем
    update_data = {
        'expiration_datetime': datetime.datetime.now().isoformat(),
        'product_id': products[0].id.__str__(),
        'external_number': str(random.randint(100000, 888888)),
    }
    data.update(update_data)
    response = await inventory_client.put(f"/api/inventory/lot/{lot_id_1}", json=data, headers=headers['superadmin'], )
    assert response.status_code == 200
    data = response.json()
    search_val = data['external_number']
    # --------------------------------
    # Поиск
    response = await inventory_client.get("/api/inventory/lot", headers=headers['superadmin'],
                                          params={'size': 100, 'search': search_val}
                                          )
    assert response.status_code == 200
    data = response.json()
    # assert len(data.get('data')) == 1
    # Удаление
    response = await inventory_client.delete(f"/api/inventory/lot/{lot_id_1}", headers=headers['superadmin'], )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_crud_quant(inventory_client, headers, stores, companies, products, lots, uoms, locations):
    """
    Проверяем rруд вокруг товаров
    """
    create_data = {
        'company_id': companies[0].id.__str__(),
        'product_id': products[0].id.__str__(),
        'store_id': stores[0].id.__str__(),
        'location_class': 'place',
        'location_id': locations['place'].id.__str__(),
        'lot_id': lots[0].id.__str__(),
        'quantity': 10.0,
        'reserved_quantity': 5,
        'expiration_datetime': datetime.datetime.now().isoformat(),
        'uom_id': uoms[0].id.__str__()
    }
    response = await inventory_client.post("/api/inventory/quant", json=create_data, headers=headers['superadmin'])
    assert response.status_code == 200
    data = response.json()
    quant_id_1 = data['id']
    # --------------------------------
    # Изменяем
    update_data = {}
    update_data.update(data)
    update_data['quantity'] = 2.5
    response = await inventory_client.put(f"/api/inventory/quant/{quant_id_1}", json=update_data,
                                          headers=headers['superadmin'], )
    assert response.status_code == 200
    # --------------------------------
    # Поиск
    response = await inventory_client.get("/api/inventory/quant", headers=headers['company_admin'])
    assert response.status_code == 200
    data = response.json()
    assert len(data.get('data')) == 7
    # Удаление
    response = await inventory_client.delete(f"/api/inventory/quant/{quant_id_1}", headers=headers['superadmin'], )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_available_quants(inventory_client, headers, stores, companies, products, lots, uoms, locations):
    """
    Проверяем получение доступных товаров
    """
    create_data = {
        'company_id': companies[0].id.__str__(),
        'product_id': products[0].id.__str__(),
        'store_id': stores[0].id.__str__(),
        'location_class': 'place',
        'location_id': locations['place'].id.__str__(),
        'lot_id': lots[0].id.__str__(),
        'quantity': 10.0,
        'reserved_quantity': 5,
        'expiration_datetime': datetime.datetime.now().isoformat(),
        'uom_id': uoms[0].id.__str__()
    }
    response = await inventory_client.post("/api/inventory/quant", json=create_data, headers=headers['superadmin'])
    assert response.status_code == 200
    data = response.json()
    quant_id_1 = data['id']

    # Получение доступных товаров
    # На вход дается схема GetAvalivleQuants
    get_available_quants = {
        'store_id': stores[0].id.__str__(),
        'product_ids': [products[0].id.__str__()],
        'exclude_id': None,
        'location_classes': ['place'],
        'location_ids': [locations['place'].id.__str__()],
        'package_ids': [],
        'location_type_ids': [],
        'lot_ids': [lots[0].id.__str__()],
        'partner_id': None,
        'quantity': 0.0
    }
    response = await inventory_client.post("/api/inventory/quant/get_available_quants", json=get_available_quants, headers=headers['company_admin'])
    assert response.status_code == 200
    data = response.json()
    assert len(data.get('data')) > 0

    # Удаление
    response = await inventory_client.delete(f"/api/inventory/quant/{quant_id_1}", headers=headers['superadmin'])
    assert response.status_code == 200
