import pytest


@pytest.mark.asyncio
async def test_list_filter_store(basic_client, headers, stores):
    """
    Проверяем что работает список с фильтрами
    """
    response = await basic_client.get(
        "/api/basic/store",
        headers=headers['company_admin'],
        params={'size': 100}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data.get('data')) == 1

    response = await basic_client.get(
        "/api/basic/store",
        headers=headers['company_admin'],
        params={'size': 100, 'search': 'Store company 1'}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data.get('data')) == 1

@pytest.mark.asyncio
async def test_update_store(basic_client, headers, stores):
    response = await basic_client.get(f"/api/basic/store/{stores[0].id.__str__()}")
    assert response.status_code == 401
    update_json = {
        'title': 'Store company 1 UPDATED',
        'address': 'Adress UPDATED',
        'external_number': 'ADRESS UPDATED'

    }
    response = await basic_client.put(f"/api/basic/store/{stores[0].id.__str__()}", json=update_json, headers=headers['company_admin'])
    assert response.status_code == 200
    data = response.json()
    assert data['title'] == update_json['title']
    assert data['address'] == update_json['address']
    assert data['external_number'] == update_json['external_number']

@pytest.mark.asyncio
async def test_crud_store(basic_client, headers, companies):
    request_data = {
        "title": "Created store",
        "address": "Created address",
        "external_number": "created external id",
        "company_id": companies[0].id.__str__(),
    }
    response = await basic_client.post("/api/basic/store", json=request_data, headers=headers['company_admin'])
    assert response.status_code == 200
    data = response.json()
    assert data['title'] == request_data['title']
    assert data['company_id'] == request_data['company_id']
    response = await basic_client.delete(f"/api/basic/store/{data['id']}", headers=headers['company_admin'])
    assert response.status_code == 200



