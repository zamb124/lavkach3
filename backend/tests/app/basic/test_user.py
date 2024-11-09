import pytest


@pytest.mark.asyncio
async def test_list_filter_company(base_client, headers):
    """
    Проверяем что работает список с фильтрами
    """
    response = await base_client.get(
        "/api/base/user",
        headers=headers['company_admin'],
        params={'size': 100, 'search': 'admin@admin.com'}
    )
    assert response.status_code == 200
    data = response.json()
    assert data['data'][0]['nickname'] == 'admin'

    response = await base_client.get(
        "/api/base/user",
        headers=headers['company_admin'],
        params={'size': 100, 'search': 'vasya'}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data.get('data')) == 2

@pytest.mark.asyncio
async def test_user_edit(base_client, headers):
    response = await base_client.get(
        "/api/base/user",
        headers=headers['company_admin'],
        params={'size': 100, 'search': 'company_support@gmail.com'}
    )
    data = response.json()
    user = data['data'][0]
    assert user['nickname'] == 'Support vasya'
    body = {
        'nickname': 'admin_edited'
    }
    user_id = user['id']
    response_edit = await base_client.put(f'/api/base/user/{user_id}', json=body, headers=headers['company_admin'])
    data = response_edit.json()
    assert data['nickname'] == 'admin_edited'
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_user_login(base_client, headers):
    body = {
        "email": "company_support@gmail.com",
        "password": "1402"
    }
    response = await base_client.post(f'/api/base/user/login', json=body)
    assert response.status_code == 200
    data = response.json()
    assert data['nickname'] in ('Support vasya', 'admin_edited')

@pytest.mark.asyncio
async def test_user_crud(base_client, headers, companies, roles):
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
    response = await base_client.post(f'/api/base/user', json=body, headers=headers['company_admin'])
    assert response.status_code == 200
    data = response.json()
    assert data['nickname'] == 'new_support_user_for_company_1'

    # чекаем что можем изменять
    user_id = data['id']
    body_edit = {
        'nickname': 'new_support_user_for_company_1_edited'
    }
    body.update(body_edit)
    response_edit = await base_client.put(f'/api/base/user/{user_id}', json=body, headers=headers['company_admin'])
    data_create = response_edit.json()
    assert data_create['nickname'] == 'new_support_user_for_company_1_edited'
    assert response.status_code == 200
    # Чекаем что появился
    response_get = await base_client.get(f'/api/base/user/{user_id}', headers=headers['company_admin'])
    data_get = response_get.json()
    assert data_get['nickname'] == 'new_support_user_for_company_1_edited'
    assert response_get.status_code == 200
    # Чекаем удаление
    response_edit = await base_client.delete(f'/api/base/user/{user_id}',  headers=headers['company_admin'])
    assert response_edit.status_code == 403

    # Чекаем адекватную ошибку при удалении если нет записи
    responce_delete_404 = await base_client.delete(f'/api/base/user/{user_id}',  headers=headers['company_admin'])
    assert responce_delete_404.status_code == 403
    # Чекаем адекватную ошибку при чтении если нет записи
    responce_get_404 = await base_client.get(f'/api/base/user/{user_id}', headers=headers['company_admin'])
    assert responce_get_404.status_code == 200




