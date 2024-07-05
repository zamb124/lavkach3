import uuid
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Any

from httpx import AsyncClient
from starlette.requests import HTTPConnection, Request
from taskiq import AsyncBroker

from app.basic import __domain__ as basic_domain
from app.inventory import __domain__ as inventory_domain
from app.bus import __domain__ as bus_domain
from core.db_config import config
from core.fastapi.adapters.action_decorator import actions
from httpx import AsyncClient as asyncclient, request

from core.fastapi.schemas import CurrentUser
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
        self.sort = sort if sort else ['id', 'created_at', 'updated_at', 'lsn']
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


domains = [
    Domain(basic_domain),
    Domain(inventory_domain),
    Domain(bus_domain)
]

class Env:
    domains: dict[str: object]
    request: HTTPConnection = None
    broker: AsyncBroker = None

    def __init__(self, domains: list, conn: HTTPConnection | AsyncClient | Request, broker: AsyncBroker = None):
        _domains = {}
        for d in domains:
            d._env = self
            _domains.update({d.name: d})
        self.request = conn
        self.domains = _domains
        self.broker = broker

    def __getitem__(self, item: str):
        for k, v in self.domains.items():
            exist_model = v.models.get(item)
            if exist_model:
                return exist_model

    @classmethod
    async def get_sudo_env(self):
        """
            Создает env путем авторизации суперюзера с походом в basic сервис
        """
        client = asyncclient()
        body = {
            "email": config.SUPERUSER_EMAIL,
            "password": config.SUPERUSER_PASSWORD
        }
        responce = await client.post(
            url=f'http://{config.BASIC_HOST}:{config.BASIC_PORT}/api/basic/user/login',
            json=body
        )
        data = responce.json()
        client = asyncclient(headers={'Authorization': data['token']})
        env = Env(domains, client)
        user = CurrentUser(id=uuid.uuid4(), is_admin=True)
        setattr(client, 'user', user)
        setattr(client, 'scope', {'env': env})
        return env

    @classmethod
    async def get_env(self):
        """
            Создает env путем ,без авторизации суперюзера
        """
        client = asyncclient()
        env = Env(domains, client)
        user = CurrentUser(id=uuid.uuid4(), is_admin=True)
        setattr(client, 'user', user)
        setattr(client, 'scope', {'env': env})
        return env


