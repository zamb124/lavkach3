from unittest import mock

import pytest
from sqlalchemy import func, select

@pytest.mark.asyncio
async def test_create_company(async_client, headers):
    request_data = {
        "title": "Test Company",
        "currency": "SAR",
        "external_number": "2131231231",
        "country": "US",
        "locale": "ru_RU"
    }
    response = await async_client.post("/api/basic/company", json=request_data)
    assert response.status_code == 401
    response = await async_client.post("/api/basic/company", json=request_data, headers=headers['superadmin'])
    assert response.status_code == 200
    data = response.json()
    assert data['title'] == "Test Company"
    assert data['lsn'] > 0

@pytest.mark.asyncio
async def test_list_company(async_client, headers, companies):
    response = await async_client.get("/api/basic/company")
    assert response.status_code == 401
    response = await async_client.get("/api/basic/company", headers=headers['superadmin'])
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 4

@pytest.mark.asyncio
async def test_update_company(async_client, headers, companies):
    response = await async_client.get(f"/api/basic/company/{companies[0].id.__str__()}")
    assert response.status_code == 401
    update_json = {
        'title': 'Great Apple',
        'currency': 'RUB',
        'country': 'RU'
    }
    response = await async_client.put(f"/api/basic/company/{companies[0].id.__str__()}", json=update_json, headers=headers['superadmin'])
    assert response.status_code == 200
    data = response.json()
    assert data['title'] == 'Great Apple'
    assert data['currency']['code'] == 'RUB'
    assert data['country']['code'] == 'RU'

@pytest.mark.asyncio
async def test_list_filter_company(async_client, headers, companies):
    response = await async_client.get("/api/basic/company", headers=headers['superadmin'], params={'size': 100, 'currency': 'RUB'})
    assert response.status_code == 200
    data = response.json()
    assert len(data.get('data')) == 1

    response = await async_client.get("/api/basic/company", headers=headers['superadmin'], params={'size': 100, 'search': 'Company 2'})
    assert response.status_code == 200
    data = response.json()
    assert len(data.get('data')) == 1
