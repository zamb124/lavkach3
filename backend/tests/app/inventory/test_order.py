import datetime

import pytest


@pytest.mark.asyncio
async def test_crud_order_type(inventory_client, headers, stores, companies, products, locations, token, ):
    """
    Проверяем rруд вокруг товаров
    """
    create_data = {
        'company_id': companies[0].id.__str__(),
        'prefix': 'IN',
        'title': 'title',
        'order_class': 'incoming',
        'allowed_zone_src_ids': [locations['partner'].id.__str__(),],
        'allowed_zone_dest_ids': [locations['place'].id.__str__(),],
        'order_type_id': None,
        'backorder_action_type': 'ask',
        'store_id': None,
        'partner_id': None,
        'reservation_method': 'at_confirm',
        'reservation_time_before': 0,
        'allowed_package_ids': [locations['package'].id.__str__(),],
        'is_homogeneity': False,
        'is_allow_create_package': True,
        'is_can_create_order_manualy': True,
        'is_overdelivery': False,
        'created_by': token['user_admin']['user_id'].__str__(),
        'edited_by': token['user_admin']['user_id'].__str__(),
        'barcode': '2132132131231',
        'strategy': 'fefo',
    }
    response = await inventory_client.post("/api/inventory/order_type", json=create_data, headers=headers['superadmin'])
    assert response.status_code == 200
    data = response.json()
    order_type_id_1 = data['id']
    #--------------------------------
    # Изменяем
    update_data = {
        'prefix': 'OUT',
        'title': 'title',
        'order_class': 'outgoing',
        'allowed_zone_src_ids': [locations['place'].id.__str__(),],
        'allowed_zone_dest_ids': [locations['partner'].id.__str__(),],
        'barcode': '999999',
    }
    data.update(update_data)
    response = await inventory_client.put(f"/api/inventory/order_type/{order_type_id_1}", json=data, headers=headers['superadmin'], )
    assert response.status_code == 200
    # --------------------------------
    # Поиск
    response = await inventory_client.get("/api/inventory/order_type", headers=headers['superadmin'], params={'size': 100, 'search': 'title'}
    )
    assert response.status_code == 200
    data = response.json()
    #assert len(data.get('data')) == 1
    # Удаление
    response = await inventory_client.delete(f"/api/inventory/order_type/{order_type_id_1}", headers=headers['superadmin'], )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_crud_order(inventory_client, token, headers, stores, companies, locations, order_types):
    """
    Проверяем rруд вокруг товаров
    """
    create_data = {
        'company_id': companies[0].id.__str__(),
        'order_type_id': order_types['inbound'].id.__str__(),
        'parent_id': None,
        'external_number': 'external id',
        'store_id': stores[0].id.__str__(),
        'partner_id': None,
        'lot_id': None,
        'origin_type': 'Purchase Order',
        'origin_number': 'Some Purchase Order Number',
        'planned_date': datetime.datetime.now().isoformat(),
        'actual_date': None,
        'created_by': token['user_admin']['user_id'].__str__(),
        'edited_by': token['user_admin']['user_id'].__str__(),
        'expiration_datetime': datetime.datetime.now().isoformat(),
        'users_ids': None,
        'description': 'description',
        'status': 'created'

    }
    response = await inventory_client.post("/api/inventory/order", json=create_data, headers=headers['superadmin'])
    assert response.status_code == 200
    data = response.json()
    order_id_1 = data['id']
    #--------------------------------
    # Изменяем
    update_data = {
        'order_type_id': order_types['inbound'].id.__str__(),
        'parent_id': None,
        'external_number': 'external id',
        'store_id': stores[0].id.__str__(),
        'partner_id': None,
        'lot_id': None,
        'origin_type': 'Purchase Order',
        'origin_number': 'Some Purchase Order Number',
        'planned_date': datetime.datetime.now().isoformat(),
        'actual_date': None,
        'created_by': token['user_admin']['user_id'].__str__(),
        'edited_by': token['user_admin']['user_id'].__str__(),
        'expiration_datetime': datetime.datetime.now().isoformat(),
        'users_ids': None,
        'description': 'description',
        'status': 'created'
    }
    response = await inventory_client.put(f"/api/inventory/order/{order_id_1}", json=update_data, headers=headers['superadmin'], )
    assert response.status_code == 200
    # --------------------------------
    # Поиск
    response = await inventory_client.get("/api/inventory/order", headers=headers['superadmin'], params={'size': 100, 'search': 'external id'}
    )
    assert response.status_code == 200
    data = response.json()
    #assert len(data.get('data')) == 1
    # Удаление
    response = await inventory_client.delete(f"/api/inventory/order/{order_id_1}", headers=headers['superadmin'], )
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_crud_move(inventory_client, token, headers, stores, companies, locations, order_types):
    """
    Перед созданием Move нужно обязятельно создать Order
    """
    create_data = {
        'company_id': companies[0].id.__str__(),
        'order_type_id': order_types['inbound'].id.__str__(),
        'parent_id': None,
        'external_number': 'external id 1',
        'store_id': stores[0].id.__str__(),
        'partner_id': None,
        'lot_id': None,
        'origin_type': 'Purchase Order',
        'origin_number': 'Some Purchase Order Number',
        'planned_date': datetime.datetime.now().isoformat(),
        'actual_date': None,
        'created_by': token['user_admin']['user_id'].__str__(),
        'edited_by': token['user_admin']['user_id'].__str__(),
        'expiration_datetime': datetime.datetime.now().isoformat(),
        'users_ids': None,
        'description': 'description',
        'status': 'created'

    }
    response = await inventory_client.post("/api/inventory/order", json=create_data, headers=headers['superadmin'])
    assert response.status_code == 200
    data = response.json()
    order_id_1 = data['id']

    #--Перед созданием Move нужно обязятельно создать Order
    create_data = {
        'company_id': companies[0].id.__str__(),
        'order_type_id': order_types['inbound'].id.__str__(),
        'parent_id': None,
        'external_number': 'external id 2',
        'store_id': stores[0].id.__str__(),
        'partner_id': None,
        'lot_id': None,
        'origin_type': 'Purchase Order',
        'origin_number': 'Some Purchase Order Number',
        'planned_date': datetime.datetime.now().isoformat(),
        'actual_date': None,
        'created_by': token['user_admin']['user_id'].__str__(),
        'edited_by': token['user_admin']['user_id'].__str__(),
        'expiration_datetime': datetime.datetime.now().isoformat(),
        'users_ids': None,
        'description': 'description',
        'status': 'created'

    }
    response = await inventory_client.post("/api/inventory/order", json=create_data,
                                                 headers=headers['superadmin'])
    assert response.status_code == 200
    data = response.json()
    order_id_1 = data['id']
    # --------------------------------

    # Изменяем
    update_data = {
        'order_type_id': order_types['inbound'].id.__str__(),
        'parent_id': None,
        'external_number': 'external id 3',
        'store_id': stores[0].id.__str__(),
        'partner_id': None,
        'lot_id': None,
        'origin_type': 'Purchase Order',
        'origin_number': 'Some Purchase Order Number',
        'planned_date': datetime.datetime.now().isoformat(),
        'actual_date': None,
        'created_by': token['user_admin']['user_id'].__str__(),
        'edited_by': token['user_admin']['user_id'].__str__(),
        'expiration_datetime': datetime.datetime.now().isoformat(),
        'users_ids': None,
        'description': 'description',
        'status': 'created'
    }
    response = await inventory_client.put(f"/api/inventory/order/{order_id_1}", json=update_data, headers=headers['superadmin'], )
    assert response.status_code == 200
    # --------------------------------
    # Поиск
    response = await inventory_client.get("/api/inventory/order", headers=headers['superadmin'], params={'size': 100, 'search': 'external id'}
    )
    assert response.status_code == 200
    data = response.json()
    #assert len(data.get('data')) == 2
    # Удаление
    response = await inventory_client.delete(f"/api/inventory/order/{order_id_1}", headers=headers['superadmin'], )
    assert response.status_code == 200