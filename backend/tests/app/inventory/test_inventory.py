import pytest
from uuid import uuid4
from app.inventory.schemas import CreateMovements, Product, Package

@pytest.fixture
def product():
    return Product(
        product_id=uuid4(),
        quantity=10.0,
        avaliable_quantity=5.0,
        lot_id=uuid4(),
        uom_id=uuid4(),
        quants=[]
    )

@pytest.fixture
def package():
    return Package(package_id=uuid4())

@pytest.mark.asyncio
async def test_create_movements_with_all_fields(inventory_client, headers, product, package):
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
async def test_create_movements_with_location_src_id_and_products(inventory_client, headers, product):
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
async def test_create_movements_with_location_dest_id_and_packages(inventory_client, headers, package):
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
async def test_create_movements_with_location_types_and_products(inventory_client, headers, product):
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
async def test_create_movements_with_location_types_and_packages(inventory_client, headers, package):
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