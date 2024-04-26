import uuid
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Any

from starlette.requests import HTTPConnection

from app.basic import __domain__ as basic_domain
from app.inventory import __domain__ as inventory_domain

from core.helpers.cache import CacheStrategy
from pydantic import BaseModel

from core.service.base import Model

if TYPE_CHECKING:

    from core.fastapi.adapters import BaseAdapter
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
    domain: 'Domain'
    schemas: Schemas
    model: Any
    sort: list = []
    cache_strategy: 'CacheStrategy' = CacheStrategy.NONE


    def __init__(self , name, _adapter, domain, schemas, model, sort=[], cache_strategy=CacheStrategy.NONE):
        self.name = name
        self._adapter = _adapter
        self.domain = domain
        self.schemas = Schemas(**schemas)
        self.model = model
        self.sort = sort
        self.cache_strategy = cache_strategy
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

class Domain:
    name: str
    models: dict[str: Model]
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
                    schemas=shemas,
                    model=value.get('model'),
                    domain=self
                )})
        self.models = models

    def __getitem__(self, item:str):
        return self.models[item]

class Env:
    domains: dict[str: object]
    request: HTTPConnection = None

    def __init__(self, domains: list, conn: HTTPConnection):
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