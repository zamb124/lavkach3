import logging
import uuid
from typing import TYPE_CHECKING

import httpx
import redis.exceptions
from fastapi import HTTPException
from starlette.datastructures import QueryParams
from starlette.requests import Request, HTTPConnection
import json as _json

from core.fastapi.adapters.action_decorator import actions
from core.helpers.cache import Cache, CacheStrategy
from core.utils.timeit import timed

if TYPE_CHECKING:
    from core.env import Env, Model, Domain

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Client(httpx.AsyncClient):
    @timed
    async def request(self, method: str, url: str, json=None, params=None, timeout=None):
        if isinstance(json, str):
            json = _json.loads(json)
        query_param_cleaned = {}
        if params:
            for name, val in params.items():
                if val:
                    query_param_cleaned.update({name: val})
        qp = QueryParams(query_param_cleaned)
        try:
            responce = await super().request(method=method, url=url, json=json, params=qp, timeout=timeout)
        except Exception as ex:
            logger.error(f'URL: {url}\n JSON: {json}\n PARAMS: {str(qp)}')
            logger.error(str(ex))
            raise HTTPException(500, detail=str(ex))
        if responce.status_code != 200:
            raise HTTPException(responce.status_code, detail=responce.json().get('detail'))
        return responce

    @timed
    async def get(self, url, *, params, kwargs=None):
        logger.info('Adapter %s %s', url, params)
        responce = await self.request('GET', url=url, params=params)
        return responce

    async def post(self, url, json, *, params, kwargs=None):
        responce = await self.request('POST', url=url, json=json, params=params)
        return responce

    async def put(self, url, json, *, params, kwargs=None):
        responce = await self.request('PUT', url=url, json=json, params=params)
        return responce

    async def delete(self, url, *, params, kwargs=None):
        responce = await self.request('DELETE', url=url, params=params)
        return responce


async def common_exception_handler(responce):
    if responce.status_code != 200:
        raise HTTPException(
            status_code=responce.status_code,
            detail=f"{str(responce.text)}"
        )
    return responce.json()


class BaseAdapter:
    """
    Универсальный адаптер, что бы ходить в другие сервисы,
    При создании нужно указать модуль, или отнаследоваться с указанием модуля
    Так же при создании можно сразу указать и модуль и модель, если нужно много раз ходить
    """
    model: 'Model'
    client: Client
    domain: 'Domain'
    request: Request
    env: 'Env'
    cache: str = Cache
    headers: dict
    protocol: str
    host: str
    port: str

    def __init__(self, conn: HTTPConnection, domain: 'Domain', model: 'Model', env: 'Env'):
        self.model = model
        self.domain = domain
        self.host = f"{self.protocol}://{self.host}:{self.port}"
        self.env = env
        self.headers = {'Authorization': conn.headers.get("Authorization") or conn.cookies.get('token') or ''}
        # if self.headers.get('Authorization'):
        self.client = Client(headers=self.headers)

    def get_actions(self):
        return actions.get(self.model.name, {})

    async def __aenter__(self):
        self.client = Client(headers=self.headers)
        return self

    async def __aexit__(self, *args, **kwargs):
        await self.client.aclose()

    async def check_in_cache(self, params, model):
        is_cached = False
        cached_data = []
        missed = []
        if model in ('locale', 'currency', 'country') or self.model.cache_strategy != CacheStrategy.FULL:
            return is_cached, cached_data, missed
        if params:
            params.pop('module', None)
            params.pop('model', None)
            id__in = params.get('id__in')
            if len(params) == 1 and id__in:
                is_cached = True
                if isinstance(id__in, uuid.UUID):
                    ids = [id__in.__str__(), ]
                else:
                    ids = id__in.split(',')
                cached_courutins = []
                for id in set(ids):
                    cached_courutins.append({
                        'promise': Cache.get_model(self.model.domain.name, model or self.model, id),
                        'id': id
                    })
                for cou in cached_courutins:
                    try:
                        cached = await cou['promise']
                    except redis.exceptions.ConnectionError as ex:
                        logger.error(f'Cache error with {model or self.model}:{cou["id"]}')
                        cached = False
                    except redis.exceptions.TimeoutError as ex:
                        logger.error(f'Cache error with {model or self.model}:{cou["id"]}')
                        cached = False
                    if cached:
                        cached_data.append(cached)
                    else:
                        missed.append(cou['id'])
        return is_cached, cached_data, missed

    async def list(self, model: str | None = None, params={}, **kwargs):

        filter = self.model.schemas.filter(**params)
        params = filter.as_params()
        is_cached, cached_data, missed = await self.check_in_cache(params, model or self.model)
        if (is_cached and missed) or not is_cached:
            if missed:
                params = QueryParams({'id__in': ','.join(missed)})
            path = f'/api/{self.model.domain.name}/{model or self.model.name}'
            responce = await self.client.get(self.host + path, params=params)
            return responce.json()
        return {
            'size': len(cached_data),
            'cursor': max([i['lsn'] for i in cached_data]),
            'data': cached_data
        }

    async def create(self, json: dict, model: str | None = None, params=None, id: uuid.UUID | None = None, **kwargs):
        path = f'/api/{self.model.domain.name}/{model or self.model}'
        responce = await self.client.post(self.host + path, json=json, params=params)
        return await common_exception_handler(responce)

    async def update(self, id: uuid.UUID, json: dict, model: str | None = None, params=None, **kwargs):
        path = f'/api/{self.model.domain.name}/{model or self.model}/{id}'
        responce = await self.client.put(self.host + path, json=json, params=params)
        return await common_exception_handler(responce)

    async def get(self, id: uuid.UUID, model: str | None = None, params=None, **kwargs):
        path = f'/api/{self.model.domain.name}/{model or self.model}/{id}'
        responce = await self.client.get(self.host + path, params=params, kwargs=kwargs)
        return await common_exception_handler(responce)

    async def view(self, id: uuid.UUID, model: str | None = None, params=None, **kwargs):
        return await self.get(id, model, params, kwargs=kwargs)

    async def delete(self, id: uuid.UUID, model: str | None = None, params=None, **kwargs):
        path = f'/api/{self.model.domain.name}/{model or self.model}/{id}'
        responce = await self.client.delete(self.host + path, params=params)
        return await common_exception_handler(responce)
