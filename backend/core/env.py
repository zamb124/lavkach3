import uuid
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Optional

from httpx import AsyncClient
from httpx import AsyncClient as asyncclient
from pydantic import BaseModel
from starlette.requests import HTTPConnection, Request
from starlette.types import ASGIApp, Scope, Receive, Send
from taskiq import AsyncBroker

from core.db_config import config
from core.fastapi.adapters.action_decorator import actions
from core.fastapi.schemas import CurrentUser
from core.helpers.cache import CacheStrategy
from .context import set_session_context, get_session_context, reset_session_context

if TYPE_CHECKING:
    from core.fastapi.adapters import BaseAdapter
    from core.service.base import Model, BaseService
from .env_domains import domains


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
        return self._service(self.domain._env.request)


class Domain:
    name: str
    models: dict[str, Model]
    _env: 'Env'
    domain_type: str
    _adapter: 'BaseAdapter' = None
    domain: 'Domain'

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

    @property
    def adapter(self):
        return self._adapter(
            conn=self._env.request,
            domain=self,
            env=self.domain._env
        )





class Env:
    domains: dict[str, Domain]
    request: HTTPConnection
    broker: AsyncBroker

    def __init__(self, domains: list, conn: HTTPConnection | AsyncClient | Request,
                 broker: AsyncBroker | None = None):
        _domains: dict = {}
        if isinstance(domains, dict):
            domains = [domains]
        for d in domains:
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
        raise KeyError(f"Model {item} not found")

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
        env = Env(domains, client)
        user = CurrentUser(id=uuid.uuid4(), is_admin=True)
        setattr(client, 'user', user)
        setattr(client, 'scope', {'env': env})
        return env

    @classmethod
    def get_env(cls):
        """
            Создает env путем, без авторизации суперюзера
        """
        client = asyncclient(headers={'Authorization': f'Bearer {config.INTERCO_TOKEN}'})
        env = Env(domains, client)
        user = CurrentUser(id=uuid.uuid4(), is_admin=True)
        setattr(client, 'user', user)
        setattr(client, 'scope', {'env': env})
        return env

    def close(self, token=None):
        reset_session_context(token)


@asynccontextmanager
async def env_context():
    token = None
    try:
        get_session_context()
    except:
        session_id = str(uuid.uuid4())
        token = set_session_context(session_id)
    # Логика инициализации
    env = Env.get_env()
    try:
        yield env
    finally:
        if token:
            env.close(token)


env: Optional[Env] = None


class EnvMidlleWare:
    """
     ENV Middleware
    """

    def __init__(self, app: ASGIApp, *args, **kwargs):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        global env
        if scope['type'] in ("http", "websocket"):
            conn = HTTPConnection(scope)
            if not env:
                env = Env(domains, conn)
                scope['env'] = env
            else:
                scope['env'] = env
                env.request = conn
        await self.app(scope, receive, send)
