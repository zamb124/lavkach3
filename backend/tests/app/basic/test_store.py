from unittest import mock

import pytest
from sqlalchemy import func, select
@pytest.mark.asyncio
async def test_list_filter_store(async_client, headers, stores):
    """
    Проверяем что работает список с фильтрами
    """
    response = await async_client.get(
        "/api/basic/project",
        headers=headers['superadmin'],
        params={'size': 100}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data.get('data')) == 2

    response = await async_client.get(
        "/api/basic/project",
        headers=headers['superadmin'],
        params={'size': 100, 'search': 'Store company 1'}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data.get('data')) == 1

@pytest.mark.asyncio
async def test_update_store(async_client, headers, stores):
    response = await async_client.get(f"/api/basic/project/{stores[0].id.__str__()}")
    assert response.status_code == 401
    update_json = {
        'title': 'Store company 1 UPDATED',
        'address': 'Adress UPDATED',
        'external_number': 'ADRESS UPDATED'

    }
    response = await async_client.put(f"/api/basic/project/{stores[0].id.__str__()}", json=update_json, headers=headers['superadmin'])
    assert response.status_code == 200
    data = response.json()
    assert data['title'] == update_json['title']
    assert data['address'] == update_json['address']
    assert data['external_number'] == update_json['external_number']

@pytest.mark.asyncio
async def test_crud_store(async_client, headers, companies):
    request_data = {
        "title": "Created project",
        "address": "Created address",
        "external_number": "created external id",
        "company_id": companies[0].id.__str__(),
    }
    response = await async_client.post("/api/basic/project", json=request_data, headers=headers['superadmin'])
    assert response.status_code == 200
    data = response.json()
    assert data['title'] == request_data['title']
    assert data['company_rel']['id'] == request_data['company_id']
    response = await async_client.delete(f"/api/basic/project/{data['id']}", headers=headers['superadmin'])
    assert response.status_code == 200



