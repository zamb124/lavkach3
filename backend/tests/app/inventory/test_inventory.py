import pytest

@pytest.mark.asyncio
async def test_create_movements_with_all_fields(inventory_client, headers, product, locations, order_types):
    data = {
        "location_src_id": uuid4(),
        "location_dest_id": uuid4(),
        "location_type_src_id": uuid4(),
        "location_type_dest_id": uuid4(),
        "products": [product],
        "packages": [package]
    }
    response = await inventory_client.post("/api/inventory/movements", json=data, headers=headers['superadmin'])
    assert response.status_code == 200
    movement = response.json()
    assert movement["location_src_id"] == str(data["location_src_id"])
    assert movement["location_dest_id"] == str(data["location_dest_id"])
    assert movement["location_type_src_id"] == str(data["location_type_src_id"])
    assert movement["location_type_dest_id"] == str(data["location_type_dest_id"])
    assert len(movement["products"]) == 1
    assert len(movement["packages"]) == 1

@pytest.mark.asyncio
async def test_create_movements_with_location_src_id_and_products(inventory_client, headers, product, locations, order_types):
    data = {
        "location_src_id": uuid4(),
        "products": [product]
    }
    response = await inventory_client.post("/api/inventory/movements", json=data, headers=headers['superadmin'])
    assert response.status_code == 200
    movement = response.json()
    assert movement["location_src_id"] == str(data["location_src_id"])
    assert movement["location_dest_id"] is None
    assert len(movement["products"]) == 1
    assert len(movement["packages"]) == 0


@pytest.mark.asyncio
async def test_create_movements_with_location_dest_id_and_packages(inventory_client, headers, package, locations, order_types):
    data = {
        "location_dest_id": uuid4(),
        "packages": [package]
    }
    response = await inventory_client.post("/api/inventory/movements", json=data, headers=headers['superadmin'])
    assert response.status_code == 200
    movement = response.json()
    assert movement["location_src_id"] is None
    assert movement["location_dest_id"] == str(data["location_dest_id"])
    assert len(movement["products"]) == 0
    assert len(movement["packages"]) == 1


@pytest.mark.asyncio
async def test_create_movements_with_location_types_and_products(inventory_client, headers, product, locations, order_types):
    data = {
        "location_type_src_id": uuid4(),
        "location_type_dest_id": uuid4(),
        "products": [product]
    }
    response = await inventory_client.post("/api/inventory/movements", json=data, headers=headers['superadmin'])
    assert response.status_code == 200
    movement = response.json()
    assert movement["location_src_id"] is None
    assert movement["location_dest_id"] is None
    assert movement["location_type_src_id"] == str(data["location_type_src_id"])
    assert movement["location_type_dest_id"] == str(data["location_type_dest_id"])
    assert len(movement["products"]) == 1
    assert len(movement["packages"]) == 0


@pytest.mark.asyncio
async def test_create_movements_with_location_types_and_packages(inventory_client, headers, package, locations, order_types):
    data = {
        "location_type_src_id": uuid4(),
        "location_type_dest_id": uuid4(),
        "packages": [package]
    }
    response = await inventory_client.post("/api/inventory/movements", json=data, headers=headers['superadmin'])
    assert response.status_code == 200
    movement = response.json()
    assert movement["location_src_id"] is None
    assert movement["location_dest_id"] is None
    assert movement["location_type_src_id"] == str(data["location_type_src_id"])
    assert movement["location_type_dest_id"] == str(data["location_type_dest_id"])
    assert len(movement["products"]) == 0
    assert len(movement["packages"]) == 1
