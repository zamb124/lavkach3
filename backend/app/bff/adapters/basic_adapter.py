from core.fastapi.adapters import BaseAdapter

class BasicAdapter(BaseAdapter):
    module = 'basic'

    async def refresh_token(self, refresh_schema):
        path = f'/api/basic/auth/refresh'
        body = {
            'token': refresh_schema.token,
            'refresh_token': refresh_schema.refresh_token
        }
        responce = await self.client.post(self.domain + path, json=body, params=None)
        return responce.json()

    async def user_company_change(self, user_id, company_id):
        path = '/api/basic/user/company_change'
        body = {
            'user_id': user_id,
            'company_id': company_id
        }
        responce = await self.client.post(self.domain + path, json=body, params=None)
        return responce.json()