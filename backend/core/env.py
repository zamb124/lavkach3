import uuid
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Any

from httpx import AsyncClient
from starlette.requests import HTTPConnection, Request

from app.basic import __domain__ as basic_domain
from app.inventory import __domain__ as inventory_domain
from core.fastapi.adapters.action_decorator import actions

from core.helpers.cache import CacheStrategy
from pydantic import BaseModel



if TYPE_CHECKING:
    from core.fastapi.adapters import BaseAdapter
    from core.service.base import Model, BaseService
    from core.db import Base


class DeleteSchema(BaseModel):
    delete_id: uuid.UUID

@dataclass
class Schemas:
    create: Any = None
    get: Any = None
    filter: Any = None
    update: Any = None
    delete: Any = None

class Model:
    name: str
    _adapter: 'BaseAdapter'
    _service: 'BaseService'
    domain: 'Domain'
    schemas: Schemas
    model: Any
    sort: list = []
    cache_strategy: 'CacheStrategy' = CacheStrategy.NONE
    actions: dict = {}


    def __init__(self , name, _adapter,_service, domain, schemas, model, sort=[], cache_strategy=CacheStrategy.NONE):
        self.name = name
        self._adapter = _adapter
        self._service = _service
        self.domain = domain
        self.schemas = Schemas(**schemas)
        self.model = model
        self.sort = sort
        self.cache_strategy = cache_strategy
        self.actions = actions.get(name, {})
    def __copy__(self):
        return self
    @property
    def adapter(self):
        return self._adapter(
            self.domain._env.request,
            domain=self.domain,
            model=self,
            env=self.domain._env
        )

    @property
    def service(self):
        return self._service(
            self.domain._env.request,
        )

class Domain:
    name: str
    models: dict[str, Model]
    _env: 'Env'
    _adapter: 'BaseAdapter' = None


    def __init__(self, domain: dict):
        self.name = domain['name']
        self._adapter = domain.get('adapter', None)
        models = {}
        for name, value in domain.items():
            if name not in ('adapter', 'name'):
                if shemas := value.get('schemas', {}):
                    shemas.update({'delete': DeleteSchema})
                models.update({name: Model(
                    name=name,
                    _adapter=self._adapter,
                    _service=value.get('service'),
                    schemas=shemas,
                    model=value.get('model'),
                    cache_strategy=value.get('cache_strategy'),
                    domain=self
                )})
        self.models = models

    def __getitem__(self, item:str):
        return self.models[item]

class Env:
    domains: dict[str: object]
    request: HTTPConnection = None

    def __init__(self, domains: list, conn: HTTPConnection | AsyncClient | Request):
        _domains = {}
        for d in domains:
            d._env = self
            _domains.update({d.name: d})
        self.request = conn
        self.domains = _domains

    def __getitem__(self, item: str):
        for k, v in self.domains.items():
            exist_model = v.models.get(item)
            if exist_model:
                return exist_model


domains = [
    Domain(basic_domain),
    Domain(inventory_domain)
]