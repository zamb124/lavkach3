from unittest import mock

import pytest
from sqlalchemy import func, select
import pytest_asyncio


async def test_list_filter_store(async_client, headers):
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
        "/api/user",
        headers=headers['superadmin'],
        params={'size': 100, 'search': 'Store company 1'}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data.get('data')) == 2


async def test_user_edit(async_client, headers):
    response = await async_client.get(
        "/api/user",
        headers=headers['superadmin'],
        params={'size': 100, 'search': 'admin@admin.com'}
    )
    data = response.json()
    user = data['data'][0]
    assert user['nickname'] == 'admin'
    body = {
        'nickname': 'admin_edited'
    }
    user_id = user['id']
    response_edit = await async_client.put(f'/api/user/{user_id}', json=body, headers=headers['superadmin'])
    data = response_edit.json()
    assert data['nickname'] == 'admin_edited'
    assert response.status_code == 200


async def test_user_login(async_client, headers):
    body = {
        "email": "company_support@gmail.com",
        "password": "1402"
    }
    response = await async_client.post(f'/api/user/login', json=body)
    assert response.status_code == 200
    data = response.json()
    assert data['nickname'] == 'Support vasya'


async def test_user_crud(async_client, headers, companies, roles):
    """
    Полный тест круда модельки
    """
    # Создаем
    body = {
        "email": "new@yandex.ru",
        "country": "US",
        "locale": "en_US",
        "phone_number": "449534771093",
        "nickname": "new_support_user_for_company_1",
        "companies": [
            companies[0].id.hex
        ],
        "roles": [
            roles.get('support').id.hex
        ],
        "password1": "1402",
        "password2": "1402"
    }
    response = await async_client.post(f'/api/user', json=body, headers=headers['company_admin'])
    assert response.status_code == 200
    data = response.json()
    assert data['nickname'] == 'new_support_user_for_company_1'

    # чекаем что можем изменять
    user_id = data['id']
    body = {
        'nickname': 'new_support_user_for_company_1_edited'
    }
    response_edit = await async_client.put(f'/api/user/{user_id}', json=body, headers=headers['superadmin'])
    data_create = response_edit.json()
    assert data_create['nickname'] == 'new_support_user_for_company_1_edited'
    assert response.status_code == 200
    # Чекаем что появился
    response_get = await async_client.get(f'/api/user/{user_id}', headers=headers['superadmin'])
    data_get = response_get.json()
    assert data_get['nickname'] == 'new_support_user_for_company_1_edited'
    assert response_get.status_code == 200
    # Чекаем удаление
    response_edit = await async_client.delete(f'/api/user/{user_id}',  headers=headers['superadmin'])
    assert response_edit.status_code == 200

    # Чекаем адекватную ошибку при удалении если нет записи
    responce_delete_404 = await async_client.delete(f'/api/user/{user_id}',  headers=headers['superadmin'])
    assert responce_delete_404.status_code == 404
    # Чекаем адекватную ошибку при чтении если нет записи
    responce_get_404 = await async_client.get(f'/api/user/{user_id}', headers=headers['superadmin'])
    assert responce_get_404.status_code == 404



