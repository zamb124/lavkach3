from unittest import mock

import pytest
from sqlalchemy import func, select

@pytest.mark.asyncio
async def test_create_company(async_client, headers, copmany):
    request_data = {
        "title": "Test Company",
        "currency": "SAR",
        "external_id": "2131231231",
        "country": "US",
        "locale": "ru_RU"
    }
    response = await async_client.post("/api/company/create", json=request_data)
    assert response.status_code == 401
    response = await async_client.post("/api/company/create", json=request_data, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data['title'] == "Test Company"
    assert data['lsn'] > 0

@pytest.mark.asyncio
async def test_list_company(async_client, headers, company):
    response = await async_client.get("/api/company")
    assert response.status_code == 401
    response = await async_client.get("/api/company", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
