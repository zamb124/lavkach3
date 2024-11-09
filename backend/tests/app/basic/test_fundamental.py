import pytest


@pytest.mark.asyncio
async def test_health(base_client, headers):
    response = await base_client.get("/api/base/health", headers=headers['superadmin'])
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_countries(base_client, headers):
    response = await base_client.get("/api/base/country", headers=headers['superadmin'])
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_countries_code(base_client, headers):
    """
    Отдает на языке пользователя все вещи
    Чекаем что под язык юзера подстраивается
    """
    response = await base_client.get("/api/base/country/ru", headers=headers['superadmin'])
    assert response.status_code == 200
    data = response.json()
    assert data.get('name') == 'Россия'

    # Чекаем что под язык юзера подстраивается
    response = await base_client.get("/api/base/country/ru", headers=headers['company_admin'])
    assert response.status_code == 200
    data = response.json()
    assert data.get('name') == 'Russia'

@pytest.mark.asyncio
async def test_currencies(base_client, headers):
    response = await base_client.get("/api/base/currency", headers=headers['superadmin'])
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_currencies_code(base_client, headers):
    """
    Отдает на языке пользователя все вещи
    Чекаем что под язык юзера подстраивается
    """
    response = await base_client.get("/api/base/currency/RUB", headers=headers['superadmin'])
    assert response.status_code == 200
    data = response.json()
    assert data.get('name') == 'российский рубль'

    # Чекаем что под язык юзера подстраивается
    response = await base_client.get("/api/base/currency/RUB", headers=headers['company_admin'])
    assert response.status_code == 200
    data = response.json()
    assert data.get('name') == 'Russian Ruble'

@pytest.mark.asyncio
async def test_locales(base_client, headers):
    """
    Проверяем что отдаем
    """
    response = await base_client.get("/api/base/locale", headers=headers['superadmin'])
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_locales_my(base_client, headers):
    """
    Проверяем что ручка отдает локаль под юзера
    """
    response = await base_client.get("/api/base/locale/my", headers=headers['superadmin'])
    assert response.status_code == 200
    data = response.json()
    assert data.get('language') == 'ru'

    response = await base_client.get("/api/base/locale/my", headers=headers['company_admin'])
    assert response.status_code == 200
    data = response.json()
    assert data.get('language') == 'en'

@pytest.mark.asyncio
async def test_locales_code(base_client, headers):
    """
    Проверяем что ручка отдает локаль под юзера
    """
    response = await base_client.get("/api/base/locale/ru", headers=headers['superadmin'])
    assert response.status_code == 200
    data = response.json()
    assert data.get('language') == 'ru'
    assert data.get('display_name') == 'русский'
