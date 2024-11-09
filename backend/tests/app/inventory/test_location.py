import pytest

@pytest.mark.asyncio
async def test_crud_location_type(inventory_client, headers, stores, companies):
    """
    Проверяем rруд вокруг товаров
    """
    create_data = {
        'company_id': companies[0].id.__str__(),
        'title': 'Partner Location',
        'location_class': 'partner'
    }
    response = await inventory_client.post("/api/inventory/location_type", json=create_data, headers=headers['superadmin'])
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
    response = await inventory_client.put(f"/api/inventory/location_type/{location_type_id_1}", json=update_data, headers=headers['superadmin'], )
    assert response.status_code == 200
    # --------------------------------
    # Поиск
    response = await inventory_client.get("/api/inventory/location_type", headers=headers['superadmin'], params={'size': 100, 'search': 'place'}
    )
    assert response.status_code == 200
    data = response.json()
    #assert len(data.get('data')) == 1
    # Удаление
    response = await inventory_client.delete(f"/api/inventory/location_type/{location_type_id_1}", headers=headers['superadmin'], )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_crud_location(inventory_client, headers, stores, companies, location_types, product_categories, uom_categories, uoms, products):
    """
    Проверяем rруд вокруг товаров
    """
    create_data = {
        'company_id': companies[0].id.__str__(),
        'title': 'place location',
        'store_id': stores[0].id.__str__(),
        'is_active': True,
        'location_type_id': location_types['place'].id.__str__(),
    }
    response = await inventory_client.post("/api/inventory/location", json=create_data, headers=headers['superadmin'])
    assert response.status_code == 200
    data = response.json()
    location_id = data['id']
    #--------------------------------
    # Изменяем локацию
    update_data = {
        'title': 'zone location',
        'is_active': False,
        'location_type_id': location_types['zone'].id.__str__(),
    }
    data.update(update_data)
    response = await inventory_client.put(f"/api/inventory/location/{location_id}", json=data, headers=headers['superadmin'], )
    assert response.status_code == 200
    # --------------------------------
    # Поиск
    response = await inventory_client.get("/api/inventory/location", headers=headers['superadmin'], params={'size': 100, 'search': 'zone location'}
    )
    assert response.status_code == 200
    data = response.json()
    #assert len(data.get('data')) == 1
    # Удаление
    response = await inventory_client.delete(f"/api/inventory/location/{location_id}", headers=headers['superadmin'], )
    assert response.status_code == 200