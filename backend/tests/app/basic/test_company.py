import pytest


@pytest.mark.asyncio
async def test_create_company(env, base_client, headers):
    request_data = {
        "title": "Test Company",
        "currency": "SAR",
        "external_number": "2131231231",
        "country": "US",
        "locale": "ru_RU"
    }
    response = await base_client.post("/api/base/company", json=request_data)
    assert response.status_code == 401
    response = await base_client.post("/api/base/company", json=request_data, headers=headers['superadmin'])
    assert response.status_code == 200
    data = response.json()
    assert data['title'] == "Test Company"
    assert data['lsn'] > 0

@pytest.mark.asyncio
async def test_list_company(base_client, headers, companies):
    response = await base_client.get("/api/base/company")
    assert response.status_code == 401
    response = await base_client.get("/api/base/company", headers=headers['superadmin'])
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 4

@pytest.mark.asyncio
async def test_update_company(base_client, headers, companies):
    response = await base_client.get(f"/api/base/company/{companies[0].id.__str__()}")
    assert response.status_code == 401
    update_json = {
        'title': 'Great Apple',
        'currency': 'RUB',
        'country': 'RU'
    }
    response = await base_client.put(f"/api/base/company/{companies[0].id.__str__()}", json=update_json, headers=headers['superadmin'])
    assert response.status_code == 200
    data = response.json()
    assert data['title'] == 'Great Apple'
    assert data['currency'] == 'RUB'
    assert data['country'] == 'RU'

@pytest.mark.asyncio
async def test_list_filter_company(base_client, headers, companies):
    response = await base_client.get("/api/base/company", headers=headers['superadmin'], params={'size': 100, 'currency__in': ['RUB']})
    assert response.status_code == 200
    data = response.json()
    assert len(data.get('data')) == 2

    response = await base_client.get("/api/base/company", headers=headers['superadmin'], params={'size': 100, 'search': 'Company 2'})
    assert response.status_code == 200
    data = response.json()
    assert len(data.get('data')) == 1
