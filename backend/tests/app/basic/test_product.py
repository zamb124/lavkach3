import pytest


@pytest.mark.asyncio
async def test_crud_product_category(basic_client, headers, stores, companies):
    """
    Проверяем rруд вокруг товаров
    """
    create_data = {
        'company_id': companies[0].id.__str__(),
        'external_number': '10001',
        'title': 'Category 1'
    }
    response = await basic_client.post("/api/basic/product_category", json=create_data, headers=headers['company_admin'])
    assert response.status_code == 200
    data = response.json()
    category_id_1 = data['id']
    # Создаем категорию с родителем
    create_data = {
        'company_id': companies[0].id.__str__(),
        'external_number': '10002',
        'title': 'Subcategory 1',
        'product_category_ids': [category_id_1, ]
    }
    response = await basic_client.post("/api/basic/product_category", json=create_data, headers=headers['company_admin'], )
    assert response.status_code == 200
    data = response.json()
    category_id_2 = data['id']
    # --------------------------------
    # Изменяем категорию
    update_data = {
        'external_number': '10003 UPDATED',
        'title': 'Subcategory 1 UPDATED ',
        'product_category_ids': []
    }
    response = await basic_client.put(f"/api/basic/product_category/{category_id_2}", json=update_data,
                                      headers=headers['company_admin'], )
    assert response.status_code == 200
    # --------------------------------
    # Поиск
    response = await basic_client.get("/api/basic/product_category", headers=headers['company_admin'],
                                      params={'size': 100, 'search': 'Subcategory'}
                                      )
    assert response.status_code == 200
    data = response.json()
    assert len(data.get('data')) == 1
    # Удаление
    response = await basic_client.delete(f"/api/basic/product_category/{category_id_2}",
                                         headers=headers['company_admin'], )
    assert response.status_code == 200
    response = await basic_client.delete(f"/api/basic/product_category/{category_id_1}",
                                         headers=headers['company_admin'], )
    assert response.status_code == 200

