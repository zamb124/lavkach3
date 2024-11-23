import datetime
import random

import pytest
from sqlalchemy.orm.sync import update


@pytest.mark.asyncio
async def test_crud_product_storage_type(inventory_client, headers, stores, companies, products, uoms, location_types,
                                         storage_types):
    """
    Проверяем rруд вокруг лота
    """
    create_data = {
        'product_id': products[1].id,
        'company_id': companies[0].id,
        'storage_uom_id': uoms[0].id,
        'allowed_storage_uom_ids': [i.id for i in uoms],
        'allowed_package_type_ids': [location_types['package'].id, ],
        'is_homogeneity': False,
        'storage_type_id': storage_types['default'].id,
        # 'partner_id': 'partner'
    }
    response = await inventory_client.post("/api/inventory/product_storage_type", json=create_data,
                                           headers=headers['superadmin'])
    assert response.status_code == 200
    data = response.json()
    product_storage_type_id_1 = data['id']
    # --------------------------------
    # Изменяем
    update_data = {
        'storage_image_url': 'https://yandex.com',
    }
    data.update(update_data)
    response = await inventory_client.put(f"/api/inventory/product_storage_type/{product_storage_type_id_1}", json=data,
                                          headers=headers['superadmin'], )
    assert response.status_code == 200
    data = response.json()
    search_val = data['id']
    # --------------------------------
    # Поиск
    response = await inventory_client.get(
        "/api/inventory/product_storage_type", headers=headers['company_admin'],
        params={'size': 100, 'product_id__in': [products[0].id]}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data.get('data')) == 1
    # Удаление
    response = await inventory_client.delete(f"/api/inventory/product_storage_type/{product_storage_type_id_1}",
                                             headers=headers['superadmin'], )
    assert response.status_code == 200
