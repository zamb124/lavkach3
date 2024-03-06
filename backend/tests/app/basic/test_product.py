from unittest import mock

import pytest
from sqlalchemy import func, select

@pytest.mark.asyncio
async def test_crud_product_category(async_client, headers, stores, companies):
    """
    Проверяем rруд вокруг товаров
    """
    create_data = {
        'company_id': companies[0].id.__str__(),
        'external_id': '10001',
        'title': 'Category 1'
    }
    response = await async_client.post("/api/product_category/create", json=create_data, headers=headers['superadmin'])
    assert response.status_code == 200
    data = response.json()
    category_id_1 = data['id']
    # Создаем категорию с родителем
    create_data = {
        'company_id': companies[0].id.__str__(),
        'external_id': '10002',
        'title': 'Subcategory 1',
        'parent_id': [category_id_1, ]
    }
    response = await async_client.post("/api/product_category/create", json=create_data, headers=headers['superadmin'], )
    assert response.status_code == 200
    data = response.json()
    category_id_2 = data['id']
    #--------------------------------
    # Изменяем категорию
    update_data = {
        'external_id': '10003 UPDATED',
        'title': 'Subcategory 1 UPDATED ',
        'parent_id': []
    }
    response = await async_client.put(f"/api/product_category/{category_id_2}", json=update_data, headers=headers['superadmin'], )
    assert response.status_code == 200
    # --------------------------------
    # Поиск
    response = await async_client.get("/api/product_category", headers=headers['superadmin'], params={'size': 100, 'search': 'Subcategory'}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data.get('data')) == 1
    # Удаление
    response = await async_client.delete(f"/api/product_category/{category_id_2}", headers=headers['superadmin'], )
    assert response.status_code == 200
    response = await async_client.delete(f"/api/product_category/{category_id_1}", headers=headers['superadmin'], )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_crud_product_storage_type(async_client, headers, stores, companies):
    """
    Проверяем rруд вокруг товаров
    """
    create_data = {
        'company_id': companies[0].id.__str__(),
        'external_id': '10001',
        'title': 'product_storage_type 1'
    }
    response = await async_client.post("/api/product_storage_type/create", json=create_data, headers=headers['superadmin'])
    assert response.status_code == 200
    data = response.json()
    product_storage_type_id_1 = data['id']
    # Создаем вторую
    create_data = {
        'company_id': companies[0].id.__str__(),
        'external_id': '10002',
        'title': 'product_storage_type 2',
    }
    response = await async_client.post("/api/product_storage_type/create", json=create_data, headers=headers['superadmin'], )
    assert response.status_code == 200
    data = response.json()
    product_storage_type_id_2 = data['id']
    #--------------------------------
    # Изменяем категорию
    update_data = {
        'external_id': '10003 UPDATED',
        'title': 'product_storage_type 1 UPDATED',
        'parent_id': []
    }
    response = await async_client.put(f"/api/product_storage_type/{product_storage_type_id_2}", json=update_data, headers=headers['superadmin'], )
    assert response.status_code == 200
    # --------------------------------
    # Поиск
    response = await async_client.get("/api/product_storage_type", headers=headers['superadmin'], params={'size': 100, 'search': 'product_storage_type 1 UPDATED'}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data.get('data')) == 1
    # Удаление
    response = await async_client.delete(f"/api/product_storage_type/{product_storage_type_id_2}", headers=headers['superadmin'], )
    assert response.status_code == 200
    response = await async_client.delete(f"/api/product_storage_type/{product_storage_type_id_1}", headers=headers['superadmin'], )
    assert response.status_code == 200