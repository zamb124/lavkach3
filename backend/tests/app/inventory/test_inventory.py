import pytest

"""
Сценарии тестирования:
Мне как кладовщику нужно перместить все товары в другую зону
Я сканирую ячейку и нажимаю (переместить все товары), выбираю зону нажимаю создать задачи
На каждый квант товара создаются задачи на перемещение в другую зону

это сценарий когда известна "ячейка" и зона назначения

"""
@pytest.mark.asyncio
async def test_create_movements_with_src_location_and_dest_zone(inventory_client, stores, headers, products, locations, location_types,
                                                order_types, product_storage_types, quants):
    data = {
        "store_id": stores[0].id,
        "location_src_zone_id": None,
        "location_src_id": locations['zone'].id,
        "location_dest_zone_id": locations['buffer'].id,
        "location_type_src_id": None,
        "location_type_dest_id": None,
    }
    response = await inventory_client.post("/api/inventory/create_movements", json=data,
                                               headers=headers['company_admin'])
    assert response.status_code == 200
    movement = response.json()
    assert movement["products"][0]['avaliable_quantity'] == 5
    assert movement["products"][0]['quantity'] == 5
    assert movement["products"][1]['avaliable_quantity'] == 15
    assert movement["products"][1]['quantity'] == 15
    assert len(movement["packages"][0]['moves']) == 1
    assert len(movement["packages"][0]['quants']) == 2


@pytest.mark.asyncio
async def test_create_movements_with_location_src_id_and_products(
        inventory_client, stores, headers, products,
        locations, location_types, order_types,
        product_storage_types, quants):
    data = {
        "store_id": stores[0].id,
        "location_src_zone_id": locations['zone'].id,
        "location_dest_zone_id": None,
        "location_type_src_id": None,
        "location_type_dest_id": None,
        "products": [{
            "product_id": products[0].id,
            "quantity": 10,
            "uom_id": products[0].uom_id,
        }]
    }
    response = await inventory_client.post("/api/inventory/create_movements", json=data, headers=headers['company_admin'])
    assert response.status_code == 200
    movement = response.json()
    assert movement["products"][0]['avaliable_quantity'] == 15
    assert movement["products"][0]['quantity'] == 10
    assert len(movement["products"][0]['moves']) == 1

@pytest.mark.asyncio
async def test_create_movements_with_location_dest_id_and_packages(inventory_client, stores, headers, products, locations, location_types,
                                                order_types, product_storage_types, quants):
    data = {
        "store_id": stores[0].id,
        "location_src_zone_id": locations['zone'].id,
        "location_dest_zone_id": locations['buffer'].id,
        "location_type_src_id": None,
        "location_type_dest_id": None,
        "packages": [{
            "package_id": locations['package'].id,
        }]
    }
    response = await inventory_client.post("/api/inventory/create_movements", json=data, headers=headers['company_admin'])
    assert response.status_code == 200
    movement = response.json()
    assert len(movement['packages'][0]['quants']) == 2
    assert len(movement['packages'][0]['moves']) == 1

@pytest.mark.asyncio
async def test_create_movements_with_location_types_and_products(inventory_client, stores, headers, products, locations, location_types,
                                                order_types, product_storage_types, quants):
    data = {
        "store_id": stores[0].id,
        "location_src_zone_id":None,
        "location_dest_zone_id": None,
        "location_type_src_id": location_types['zone'].id,
        "location_type_dest_id": location_types['buffer'].id,
        "products": [{
            "product_id": products[0].id,
            "quantity": 10,
            "uom_id": products[0].uom_id,
        }]
    }
    response = await inventory_client.post("/api/inventory/create_movements", json=data, headers=headers['company_admin'])
    assert response.status_code == 200
    movement = response.json()
    assert movement["products"][0]['avaliable_quantity'] == 30
    assert movement["products"][0]['quantity'] == 10
    assert len(movement["packages"][0]['moves']) == 1
    assert len(movement["packages"][0]['quants']) == 2

@pytest.mark.asyncio
async def test_create_movements_with_location_types_and_packages(inventory_client, stores, headers, products, locations, location_types,
                                                order_types, product_storage_types, quants):
    data = {
        "store_id": stores[0].id,
        "location_src_zone_id": locations['zone'].id,
        "location_dest_zone_id": locations['buffer'].id,
        "location_type_src_id": None,
        "location_type_dest_id": None,
        "packages": [{
            "package_id": locations['package'].id,
        }]
    }
    response = await inventory_client.post("/api/inventory/create_movements", json=data, headers=headers['company_admin'])
    assert response.status_code == 200
    movement = response.json()
    assert len(movement['packages'][0]['quants']) == 2
    assert len(movement['packages'][0]['moves']) == 1
