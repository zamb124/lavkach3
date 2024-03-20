import uuid

import httpx
from fastapi import HTTPException
from starlette.requests import Request, HTTPConnection

from core.config import config

class Client(httpx.AsyncClient):
    async def request(self, method, url, json=None, params=None, timeout=None):
        responce = await super().request(method=method, url=url, json=json, params=params, timeout=timeout)
        if responce.status_code == 401:
            raise HTTPException(status_code=401, detail="Authorization error")
        return responce

    async def get(self, url, *, params):
        responce = await self.request('GET', url=url, params=params)
        return responce

    async def post(self, url,json, *, params):
        responce = await self.request('POST', url=url, json=json, params=params)
        return responce
    async def put(self, url, *, params):
        responce = await self.request('PUT', url=url, params=params)
        return responce

    async def delete(self, url, *, params):
        responce = await self.request('DELETE', url=url, params=params)
        return responce


class BaseAdapter:
    """
    Универсальный адаптер, что бы ходить в другие сервисы,
    При создании нужно указать модуль, или отнаследоваться с указанием модуля
    Так же при создании можно сразу указать и модуль и модель, если нужно много раз ходить
    """
    headers: dict
    module: str
    model: str = None
    client: Client = None
    domain: str = None
    request: Request

    def __init__(self, conn: HTTPConnection, module: str = None, model: str = None):
        if module:
            self.module = module
        if model:
            self.model = model
        self.domain = f"http://{config.services[self.module]['DOMAIN']}:{config.services[self.module]['PORT']}"
        self.headers = {'Authorization': conn.headers.get("Authorization") or conn.cookies.get('token')}

    async def __aenter__(self):
        self.client = Client(headers=self.headers)
        return self

    async def __aexit__(self, *args, **kwargs):
        await self.client.aclose()

    async def list(self, model: str = None, params=None, **kwargs):
        path = f'/api/{self.module}/{model or self.model}'
        responce = await self.client.get(self.domain + path, params=params)
        data = responce.json()
        return data

    async def create(self, json: dict, model: str = None, params=None, **kwargs):
        path = f'/api/{self.module}/{model or self.model}'
        responce = await self.client.post(self.domain + path, json=json, params=params)
        data = responce.json()
        return data

    async def update(self, id: uuid.UUID, json: dict, model: str = None, params=None, **kwargs):
        path = f'/api/{self.module}/{model or self.model}/{id}'
        responce = await self.client.put(self.domain + path, json=json, params=params)
        data = responce.json()
        return data

    async def get(self, id: uuid.UUID, model: str = None, params=None, **kwargs):
        path = f'/api/{self.module}/{model or self.model}/{id}'
        responce = await self.client.get(self.domain + path, params=params)
        data = responce.json()
        return data

    async def delete(self, id: uuid.UUID, model: str = None, params=None, **kwargs):
        path = f'/api/{self.module}/{model or self.model}/{id}'
        responce = await self.client.delete(self.domain + path, params=params)
        data = responce.json()
        return data
