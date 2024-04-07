import uuid

import httpx
from fastapi import HTTPException
from starlette.datastructures import QueryParams
from starlette.requests import Request, HTTPConnection
from fastapi.exceptions import RequestValidationError
from core.config import config

import logging

logging.basicConfig(level=logging.INFO)

class Client(httpx.AsyncClient):
    async def request(self, method: str, url: str, json=None, params=None, timeout=None):
        query_param_cleaned = {}
        if params:
            for name, val in params.items():
                if val:
                    query_param_cleaned.update({name: val})
        qp = QueryParams(query_param_cleaned)
        print('LOG::::',method, url, json, params)

        responce = await super().request(method=method, url=url, json=json, params=qp, timeout=timeout)

        if responce.status_code != 200:
            raise HTTPException(responce.status_code, detail=responce.json())
        return responce

    async def get(self, url, *, params):
        responce = await self.request('GET', url=url, params=params)
        return responce

    async def post(self, url,json, *, params):
        responce = await self.request('POST', url=url, json=json, params=params)
        return responce
    async def put(self, url, json, *, params):
        responce = await self.request('PUT', url=url, json=json, params=params)
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
    client: Client = None
    domain: str = None
    request: Request

    def __init__(self, conn: HTTPConnection, config: dict, module: str = None, model: str = None):
        if module:
            self.module = module
        if model:
            self.model = model
        self.domain = f"http://{config['DOMAIN']}:{config['PORT']}"
        self.headers = {'Authorization': conn.headers.get("Authorization") or conn.cookies.get('token')}
        if self.headers.get('Authorization'):
            self.client = Client(headers=self.headers)

    async def __aenter__(self):
        self.client = Client(headers=self.headers)
        return self

    async def __aexit__(self, *args, **kwargs):
        await self.client.aclose()

    async def common_exception_handler(self, responce):
        if responce.status_code != 200:
            raise HTTPException(
                status_code=responce.status_code,
                detail=f"{str(responce.text)}"
            )
        return responce.json()

    async def list(self, model: str = None, params=None, **kwargs):
        path = f'/api/{self.module}/{model or self.model}'
        responce = await self.client.get(self.domain + path, params=params)
        return await self.common_exception_handler(responce)

    async def create(self, json: dict, model: str = None, params=None,id:uuid.UUID = None, **kwargs):
        path = f'/api/{self.module}/{model or self.model}'
        responce = await self.client.post(self.domain + path, json=json, params=params)
        return await self.common_exception_handler(responce)

    async def update(self, id: uuid.UUID, json: dict, model: str = None, params=None, **kwargs):
        path = f'/api/{self.module}/{model or self.model}/{id}'
        responce = await self.client.put(self.domain + path, json=json, params=params)
        return await self.common_exception_handler(responce)

    async def get(self, id: uuid.UUID, model: str = None, params=None, **kwargs):
        path = f'/api/{self.module}/{model or self.model}/{id}'
        responce = await self.client.get(self.domain + path, params=params)
        return await self.common_exception_handler(responce)

    async def delete(self, id: uuid.UUID, model: str = None, params=None, **kwargs):
        path = f'/api/{self.module}/{model or self.model}/{id}'
        responce = await self.client.delete(self.domain + path, params=params)
        return await self.common_exception_handler(responce)
