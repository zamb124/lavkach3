from unittest import mock

import pytest
from sqlalchemy import func, select
#from tests.conftest import *
@pytest.mark.asyncio
async def test_crud_location_type(async_inventory_client, headers, stores, companies):
    """
    Проверяем rруд вокруг товаров
    """
    create_data = {
        'company_id': companies[0].id.__str__(),
        'title': 'Partner Location',
        'location_class': 'partner'
    }
    response = await async_inventory_client.post("/api/inventory/location_type/create", json=create_data, headers=headers['superadmin'])
    assert response.status_code == 200
    data = response.json()
    location_type_id_1 = data['id']
    #--------------------------------
    # Изменяем категорию
    update_data = {
        'company_id': companies[0].id.__str__(),
        'location_class': 'place',
        'title': 'Place Location',
    }
    response = await async_inventory_client.put(f"/api/inventory/location_type/{location_type_id_1}", json=update_data, headers=headers['superadmin'], )
    assert response.status_code == 200
    # --------------------------------
    # Поиск
    response = await async_inventory_client.get("/api/inventory/location_type", headers=headers['superadmin'], params={'size': 100, 'search': 'Place'}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data.get('data')) == 1
    # Удаление
    response = await async_inventory_client.delete(f"/api/inventory/location_type/{location_type_id_1}", headers=headers['superadmin'], )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_crud_location(async_inventory_client, headers, stores, companies, location_types, product_categories, product_storage_types, uom_categories, uoms, products):
    """
    Проверяем rруд вокруг товаров
    """
    create_data = {
        'company_id': companies[0].id.__str__(),
        'title': 'place location',
        'store_id': stores[0].id.__str__(),
        'active': True,
        'location_type_id': location_types['place'].id.__str__(),
    }
    response = await async_inventory_client.post("/api/inventory/location/create", json=create_data, headers=headers['superadmin'])
    assert response.status_code == 200
    data = response.json()
    location_id = data['id']
    #--------------------------------
    # Изменяем локацию
    update_data = {
        'title': 'zone location',
        'active': False,
        'location_type_id': location_types['zone'].id.__str__(),
    }
    response = await async_inventory_client.put(f"/api/inventory/location/{location_id}", json=update_data, headers=headers['superadmin'], )
    assert response.status_code == 200
    # --------------------------------
    # Поиск
    response = await async_inventory_client.get("/api/inventory/location", headers=headers['superadmin'], params={'size': 100, 'search': 'zone location'}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data.get('data')) == 1
    # Удаление
    response = await async_inventory_client.delete(f"/api/inventory/location/{location_id}", headers=headers['superadmin'], )
    assert response.status_code == 200