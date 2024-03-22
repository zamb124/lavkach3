from unittest import mock

import pytest
from sqlalchemy import func, select

@pytest.mark.asyncio
async def test_health(async_client, headers):
    response = await async_client.get("/api/basic/health", headers=headers['superadmin'])
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_countries(async_client, headers):
    response = await async_client.get("/api/basic/country", headers=headers['superadmin'])
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_countries_code(async_client, headers):
    """
    Отдает на языке пользователя все вещи
    Чекаем что под язык юзера подстраивается
    """
    response = await async_client.get("/api/basic/country/ru", headers=headers['superadmin'])
    assert response.status_code == 200
    data = response.json()
    assert data.get('name') == 'Россия'

    # Чекаем что под язык юзера подстраивается
    response = await async_client.get("/api/basic/country/ru", headers=headers['company_admin'])
    assert response.status_code == 200
    data = response.json()
    assert data.get('name') == 'Russia'

@pytest.mark.asyncio
async def test_currencies(async_client, headers):
    response = await async_client.get("/api/basic/currency", headers=headers['superadmin'])
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_currencies_code(async_client, headers):
    """
    Отдает на языке пользователя все вещи
    Чекаем что под язык юзера подстраивается
    """
    response = await async_client.get("/api/basic/currency/RUB", headers=headers['superadmin'])
    assert response.status_code == 200
    data = response.json()
    assert data.get('name') == 'российский рубль'

    # Чекаем что под язык юзера подстраивается
    response = await async_client.get("/api/basic/currency/RUB", headers=headers['company_admin'])
    assert response.status_code == 200
    data = response.json()
    assert data.get('name') == 'Russian Ruble'

@pytest.mark.asyncio
async def test_locales(async_client, headers):
    """
    Проверяем что отдаем
    """
    response = await async_client.get("/api/basic/locale", headers=headers['superadmin'])
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_locales_my(async_client, headers):
    """
    Проверяем что ручка отдает локаль под юзера
    """
    response = await async_client.get("/api/basic/locale/my", headers=headers['superadmin'])
    assert response.status_code == 200
    data = response.json()
    assert data.get('language') == 'ru'

    response = await async_client.get("/api/basic/locale/my", headers=headers['company_admin'])
    assert response.status_code == 200
    data = response.json()
    assert data.get('language') == 'en'

@pytest.mark.asyncio
async def test_locales_code(async_client, headers):
    """
    Проверяем что ручка отдает локаль под юзера
    """
    response = await async_client.get("/api/basic/locale/ru", headers=headers['superadmin'])
    assert response.status_code == 200
    data = response.json()
    assert data.get('language') == 'ru'
    assert data.get('display_name') == 'русский'
