import datetime

import pytest


@pytest.mark.asyncio
async def test_crud_lot(async_inventory_client, headers, stores, companies, products):
    """
    Проверяем rруд вокруг товаров
    """
    create_data = {
        'company_id': companies[0].id.__str__(),
        'expiration_date': datetime.datetime.now().isoformat(),
        'product_id': products[0].id.__str__(),
        'external_number': '1000001',
        #'partner_id': 'partner'
    }
    response = await async_inventory_client.post("/api/inventory/lot", json=create_data, headers=headers['superadmin'])
    assert response.status_code == 200
    data = response.json()
    lot_id_1 = data['id']
    #--------------------------------
    # Изменяем
    update_data = {
        'expiration_date': datetime.datetime.now().isoformat(),
        'product_id': products[0].id.__str__(),
        'external_number': '1000002',
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
    response = await async_inventory_client.post("/api/inventory/quant", json=create_data, headers=headers['superadmin'])
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
    response = await async_inventory_client.get("/api/inventory/quant", headers=headers['superadmin'], params={'size': 100, 'created_at_gte': '2023-01-01'}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data.get('data')) == 1
    # Удаление
    response = await async_inventory_client.delete(f"/api/inventory/quant/{lot_id_1}", headers=headers['superadmin'], )
    assert response.status_code == 200