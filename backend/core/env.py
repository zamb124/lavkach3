import uuid
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Any

from httpx import AsyncClient
from starlette.requests import HTTPConnection, Request
from taskiq import AsyncBroker


from core.db.session import set_session_context
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
from .core_apps.base import __domain__ as base_domain
from .core_apps.bus import __domain__ as bus_domain

class DeleteSchema(BaseModel):
    delete_id: uuid.UUID


@dataclass
class Schemas:
    create: Any = None
    get: Any = None
    filter: Any = None
    update: Any = None
    delete: Any = None


class Model:  # type: ignore
    name: str
    _adapter: 'BaseAdapter'
    _service: 'BaseService'
    domain: 'Domain'
    schemas: Schemas
    model: Any
    sort: list = []
    cache_strategy: 'CacheStrategy' = CacheStrategy.NONE
    actions: dict = {}

    def __init__(self, name, _adapter, _service, domain, schemas, model, sort=[], cache_strategy=CacheStrategy.NONE):
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
            conn=self.domain._env.request,
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
    domain_type: str
    _adapter: 'BaseAdapter' = None


    def __init__(self, domain: dict, domain_type='EXTERNAL'):
        self.name = domain['name']
        self.domain_type = domain_type
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

    def __getitem__(self, item: str):
        return self.models[item]

core_domains = [base_domain, bus_domain]

class Env:
    domains: dict[str, Domain]
    request: HTTPConnection
    broker: AsyncBroker

    def __init__(self, domains: list | dict, conn: HTTPConnection | AsyncClient | Request, broker: AsyncBroker | None = None):
        _domains: dict = {}
        if isinstance(domains, dict):
            domains = [domains]
        for d in domains+core_domains:
            domain_type: str = 'EXTERNAL'
            if isinstance(d, tuple):
                domain_type = d[1]
                d = d[0]
            if isinstance(d, dict):
                d = Domain(d, domain_type)
            d._env = self
            _domains.update({d.name: d})
        self.request = conn  # type: ignore
        self.domains = _domains
        self.broker = broker  # type: ignore

    def __getitem__(self, item: str):
        for k, v in self.domains.items():
            exist_model = v.models.get(item)
            if exist_model:
                return exist_model
        raise KeyError

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
            url=f'http://{config.BASE_HOST}:{config.BASE_PORT}/api/base/user/login',
            json=body
        )
        data = responce.json()
        client = asyncclient(headers={'Authorization': data['token']})
        env = Env(core_domains, client)
        user = CurrentUser(id=uuid.uuid4(), is_admin=True)
        setattr(client, 'user', user)
        setattr(client, 'scope', {'env': env})
        return env

    @classmethod
    def get_env(cls):
        """
            Создает env путем ,без авторизации суперюзера
        """
        session_id = str(uuid.uuid4())
        set_session_context(session_id=session_id) # Делаем сессию для env, если она без реквеста
        client = asyncclient(headers={'Authorization': f'Bearer {config.INTERCO_TOKEN}'})
        env = Env(core_domains, client)
        user = CurrentUser(id=uuid.uuid4(), is_admin=True)
        setattr(client, 'user', user)
        setattr(client, 'scope', {'env': env})
        return env
