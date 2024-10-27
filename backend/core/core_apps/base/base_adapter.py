import json
from uuid import UUID

from .base_config import config
from ...fastapi.adapters import BaseAdapter
from ...fastapi.adapters.action_decorator import action


class BaseAdapter(BaseAdapter):
    module = 'base'
    protocol = config.APP_PROTOCOL
    port = config.APP_PORT
    host = config.APP_HOST



    async def refresh_token(self, refresh_schema):
        path = f'/api/base/user/refresh'
        body = {
            'token': refresh_schema.token,
            'refresh_token': refresh_schema.refresh_token
        }
        responce = await self.client.post(self.host + path, json=body, params=None)
        return responce.json()

    async def user_company_change(self, user_id, company_id):
        path = '/api/base/user/company_change'
        body = {
            'user_id': user_id.__str__(),
            'company_id': company_id.__str__()
        }
        responce = await self.client.post(self.host + path, json=body, params=None)
        return responce.json()

    async def user_locale_change(self, user_id, locale):
        path = '/api/base/user/locale_change'
        body = {
            'user_id': user_id.__str__(),
            'locale': locale
        }
        responce = await self.client.post(self.host + path, json=body, params=None)
        return responce.json()

    async def login(self, username, password):
        path = f'/api/base/user/login'
        body = {
            'email': username,
            'password': password
        }
        responce = await self.client.post(self.host + path, json=body, params=None)
        return responce.json()

    async def logout(self, user_id):
        path = f'/api/base/user/logout'
        body = {
            'user_id': user_id.__str__(),
        }
        responce = await self.client.post(self.host + path, json=body, params=None)
        return responce.json()

    async def dropdown_ids(self, model: str, id: str, itemlink: str, is_named=False, message=None):
        """
            Виджет на вход получает модуль-модель-ид- и обратную ссылку если нужно, если нет будет /module/model/{id}
            _named означает, что так же будет отдат name для отрисовки на тайтле кнопки
        """
        data = await self.list(model=model)
        items = []
        title = False
        for i in data.get('data'):
            if i['id'] == id:
                title = i['title']
            items.append({
                'title': i['title'],
                'url': f'{itemlink}/{i["id"]}' if itemlink else f'/{self.module}/{model}/{i["id"]}'
                # Если нет ссылки то отдаем ссылку на обьекты по умолчанию (form)
            })
        return {
            'model': model,
            'module': self.module,
            'title': title,
            'message': message,
            'items': items
        }

    async def product_by_barcode(self, barcode):
        path = f'/api/base/product/barcode/{barcode}'
        responce = await self.client.get(self.host + path, params=None)
        return self.env['product'].schemas.get(**responce.json())

    async def permissions(self, user_id: UUID):
        path = f'/api/base/user/{user_id}/permissions'
        responce = await self.client.get(self.host + path, params=None)
        return responce.json()

    @action(model='project', multiple=False, permits=[])
    async def action_assign_store(self, payload: dict | str):
        """Метод прикрепления к складу """
        path = f'/api/base/project/assign_store'
        if isinstance(payload, str):
            payload = json.loads(payload)
        responce = await self.client.post(self.host + path, json=payload, params={})
        return responce.json()