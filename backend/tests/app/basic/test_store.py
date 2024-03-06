from unittest import mock

import pytest
from sqlalchemy import func, select
@pytest.mark.asyncio
async def test_list_filter_store(async_client, headers, stores):
    """
    Проверяем что работает список с фильтрами
    """
    response = await async_client.get(
        "/api/store",
        headers=headers['superadmin'],
        params={'size': 100}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data.get('data')) == 2

    response = await async_client.get(
        "/api/store",
        headers=headers['superadmin'],
        params={'size': 100, 'search': 'Store company 1'}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data.get('data')) == 1

@pytest.mark.asyncio
async def test_update_store(async_client, headers, stores):
    response = await async_client.get(f"/api/store/{stores[0].id.__str__()}")
    assert response.status_code == 401
    update_json = {
        'title': 'Store company 1 UPDATED',
        'address': 'Adress UPDATED',
        'external_id': 'ADRESS UPDATED'

    }
    response = await async_client.put(f"/api/store/{stores[0].id.__str__()}", json=update_json, headers=headers['superadmin'])
    assert response.status_code == 200
    data = response.json()
    assert data['title'] == update_json['title']
    assert data['address'] == update_json['address']
    assert data['external_id'] == update_json['external_id']

@pytest.mark.asyncio
async def test_crud_store(async_client, headers, companies):
    request_data = {
        "title": "Created store",
        "address": "Created address",
        "external_id": "created external id",
        "company_id": companies[0].id.__str__(),
    }
    response = await async_client.post("/api/store/create", json=request_data, headers=headers['superadmin'])
    assert response.status_code == 200
    data = response.json()
    assert data['title'] == request_data['title']
    assert data['company']['id'] == request_data['company_id']
    response = await async_client.delete(f"/api/store/{data['id']}", headers=headers['superadmin'])
    assert response.status_code == 200



