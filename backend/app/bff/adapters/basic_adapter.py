import httpx
from app.bff.bff_config import config
from fastapi import Request
import uuid
class BasicAdapter:
    headers: dict
    session: httpx.AsyncClient = None
    basic_url: str = f"http://{config.services['basic']['DOMAIN']}:{config.services['basic']['PORT']}"
    path = '/api/company'
    store_base_path = '/api/store'
    def __init__(self, request: Request):
        self.headers = {'Authorization': request.headers.get('Authorization') or request.cookies.get('token')}
    async def __aenter__(self):
        self.session = httpx.AsyncClient(headers=self.headers)
        return self

    async def __aexit__(self, *args, **kwargs):
        await self.session.aclose()

    async def get_company_list(self, params=None, **kwargs):
        responce = await self.session.get(self.basic_url + self.path, params=params)
        return responce.json()

    async def get_company(self, company_id: uuid.UUID):
        async with self.session.get(self.basic_url + self.path +f'/{company_id.__str__()}') as resp:
            data = await resp.json()
        return data

    # Stores
    async def get_stores(self, params=None, **kwargs):
        responce = await self.session.get(self.basic_url + self.store_base_path, params=params)
        return responce.json()

    async def store(self, params=None, *args, **kwargs):
        responce = await self.session.get(self.basic_url + self.store_base_path, params=params)
        return responce.json()
