import asyncio
from typing import Type, Dict, Any, List

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from starlette.requests import Request

from app.basic.company.models import Company
from app.basic.company.schemas import CompanyCreateScheme
from app.basic.company.services import CompanyService
from app.basic.user.models import User
from app.basic.user.schemas import UserCreateScheme, RoleCreateScheme, LoginResponseSchema
from app.basic.user.services import UserService
from app.basic.user.services.role_service import RoleService
from app.server import app
from core.config import config
from core.db.session import Base
from core.fastapi.schemas import CurrentUser
from core.permissions import permits
from core.service import base
from core.service.base import ModelType


@pytest.fixture(scope="session")
def event_loop() -> asyncio.AbstractEventLoop:
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def engine():
    engine = create_async_engine(config.TEST_WRITER_DB_URL)
    yield engine
    engine.sync_engine.dispose()


@pytest_asyncio.fixture(scope="session")
async def prepare_db():
    create_db_engine = create_async_engine(
        config.POSTGRES_TEST_DATABASE_URL,
        isolation_level="AUTOCOMMIT",
    )
    async with create_db_engine.begin() as connection:
        await connection.execute(
            text(
                "drop database if exists {name};".format(
                    name=config.DB_NAME_TEST
                )
            ),
        )
        await connection.execute(
            text("create database {name};".format(name=config.DB_NAME_TEST)),
        )


@pytest_asyncio.fixture(scope="session")
async def db_session(engine) -> AsyncSession:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)
        TestingSessionLocal = sessionmaker(
            expire_on_commit=False,
            class_=AsyncSession,
            bind=engine,
        )
        async with TestingSessionLocal(bind=connection) as session:
            yield session
            await session.flush()
            await session.rollback()


@pytest.fixture(scope="session")
def override_get_db(prepare_db, db_session: AsyncSession):
    async def _override_get_db():
        yield db_session

    return _override_get_db


@pytest_asyncio.fixture(scope="session")
def ovveride_base_init(db_session):
    def __init__(self, request: Request | CurrentUser | None, model: Type[ModelType], session=None):
        if isinstance(request, CurrentUser):
            self.user = request
        elif isinstance(request, Request):
            self.user = request.user
        self.model = model
        self.session = db_session

    return __init__


@pytest_asyncio.fixture(scope="session")
async def async_client(override_get_db, db_session, ovveride_base_init):
    base.BaseService.__init__ = ovveride_base_init
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def user_admin(db_session: AsyncSession) -> User:
    user = UserCreateScheme(**{
        "email": "admin@admin.com",
        "nickname": "admin",
        "is_admin": True,
        "password1": "1402",
        "password2": "1402"
    })
    user_db = await UserService().sudo().create(user)
    admin_user = CurrentUser(**user_db.__dict__)
    yield admin_user
    await db_session.delete(user_db)
    await db_session.commit()


@pytest_asyncio.fixture
async def companies(db_session: AsyncSession, user_admin) -> Company:
    company1 = CompanyCreateScheme(title="Test company 1", currency='USD')
    company2 = CompanyCreateScheme(title="Test company 2", currency='RUB')
    company1_db = await CompanyService(user_admin).create(company1)
    company2_db = await CompanyService(user_admin).create(company2)
    yield [company1_db, company2_db]
    await db_session.delete(company1_db)
    await db_session.delete(company2_db)
    await db_session.commit()


@pytest_asyncio.fixture
async def roles(db_session: AsyncSession, companies, user_admin) -> User:
    permission_allow = [
        "user_create", 'user_edit', 'user_list', 'user_get', 'partner_create',
        'partner_edit', 'partner_list', 'partner_delete', 'partner_get',
        'company_create', 'company_edit', 'company_list', 'company_get',
        'uom_create', 'uom_edit', 'uom_list', 'uom_delete', 'uom_get']
    role_admin = RoleCreateScheme(title="admin", permissions_allow=list(permits.keys()), company_id=companies[0].id)
    role_admin_db = await RoleService(user_admin).create(role_admin)
    role_support = RoleCreateScheme(title="support", permissions_allow=permission_allow, company_id=companies[0].id,
                                    parents=[role_admin_db.id])
    role_support_db = await RoleService(user_admin).create(role_support)
    yield {'admin': role_admin_db, 'support': role_support_db}
    await db_session.delete(role_admin_db)
    await db_session.delete(role_support_db)
    await db_session.commit()


@pytest_asyncio.fixture
async def users(db_session: AsyncSession, companies, roles, user_admin) -> User:
    company_admin = UserCreateScheme(**{
        "email": "company_admin@gmail.com",
        "nickname": "Admin vasya",
        "is_admin": False,
        "companies": [
            companies[0].id
        ],
        "roles": [
            roles.get('admin').id
        ],
        "password1": "1402",
        "password2": "1402"
    })
    company_support = UserCreateScheme(**{
        "email": "company_support@gmail.com",
        "nickname": "Support vasya",
        "is_admin": False,
        "companies": [
            companies[0].id
        ],
        "roles": [
            roles.get('support').id
        ],
        "password1": "1402",
        "password2": "1402"
    })
    company_admin_db = await UserService(user_admin).create(company_admin)
    company_support_db = await UserService(user_admin).create(company_support)
    yield {'company_admin': company_admin_db, 'company_support': company_support_db}
    await db_session.delete(company_admin_db)
    await db_session.delete(company_support_db)
    await db_session.commit()


@pytest_asyncio.fixture
async def token(db_session: AsyncSession, users: User, user_admin) -> dict[str, Any]:
    user_admin = await UserService(None).login('admin@admin.com', '1402')
    company_admin = await UserService(None).login(users.get('company_admin').email, users.get('company_admin').password)
    company_support = await UserService(None).login(users.get('company_support').email,
                                                    users.get('company_support').password)
    return {
        'user_admin': user_admin,
        'company_admin': company_admin,
        'company_support': company_support
    }


@pytest_asyncio.fixture
async def headers(token) -> dict:
    return {
        'superadmin': {'Authorization': token['user_admin']['token']},
        'company_admin': {'Authorization': token['company_admin']['token']},
        'company_support': {'Authorization': token['company_support']['token']}
    }


@pytest.mark.asyncio
async def test_health(async_client, headers):
    response = await async_client.get("/api/fundamental/health", headers=headers['superadmin'])
    assert response.status_code == 200
