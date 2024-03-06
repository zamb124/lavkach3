import asyncio
from datetime import datetime
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
from app.basic.product.models import ProductType
from app.basic.store.schemas import StoreCreateScheme
from app.basic.store.services import StoreService
from app.basic.product.services import ProductCategoryService, ProductStorageTypeService, ProductService
from app.basic.product.schemas import ProductCategoryCreateScheme, ProductStorageTypeCreateScheme, ProductCreateScheme
from app.basic.uom.models import UomType
from app.basic.uom.schemas import UomCategoryCreateScheme, UomCreateScheme
from app.basic.uom.services import UomCategoryService, UomService
from app.basic.user.models import User
from app.basic.user.schemas import UserCreateScheme, RoleCreateScheme, LoginResponseSchema
from app.basic.user.services import UserService
from app.basic.user.services.role_service import RoleService
from app.basic.basic_server import app
from app.inventory.inventory_server import app as basic_app
from app.inventory.location.enums import LocationClass, PutawayStrategy
from app.inventory.location.schemas import LocationTypeCreateScheme, LocationCreateScheme
from app.inventory.location.services import LocationService, LocationTypeService
from app.inventory.quant.schemas import LotCreateScheme
from app.inventory.quant.services import LotService
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
    db_name_base = config.DB_NAME_TEST
    for i in range(5):
        db_name = f'{db_name_base}_{i}'
        try:
            async with create_db_engine.begin() as connection:
                await connection.execute(
                    text(
                        "drop database if exists {name};".format(
                            name=db_name
                        )
                    ),
                )
            await connection.execute(
                text("create database {name};".format(name=db_name)),
            )
        except Exception as ex:
            continue



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

@pytest_asyncio.fixture(scope="session")
async def async_inventory_client(override_get_db, db_session, ovveride_base_init):
    base.BaseService.__init__ = ovveride_base_init
    async with AsyncClient(app=basic_app, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def user_admin(db_session: AsyncSession) -> User:
    user = UserCreateScheme(**{
        "email": "admin@admin.com",
        "nickname": "admin",
        "locale": "RU",
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
async def stores(db_session: AsyncSession, user_admin, companies) -> Company:
    store1 = StoreCreateScheme(title="Store company 1", company_id=companies[0].id, address='addres 1')
    store2 = StoreCreateScheme(title="Store company 2",  company_id=companies[1].id, address='addres 1')
    store1_db = await StoreService(user_admin).create(store1)
    store2_db = await StoreService(user_admin).create(store2)
    yield [store1_db, store2_db]
    await db_session.delete(store1_db)
    await db_session.delete(store2_db)
    await db_session.commit()

@pytest_asyncio.fixture
async def product_categories(db_session: AsyncSession, user_admin, companies) -> Company:
    product_category1 = await ProductCategoryService(user_admin).create(ProductCategoryCreateScheme(**{
        'company_id': companies[0].id.__str__(),
        'title': 'Some Category 1'
    }))
    product_category2 = await ProductCategoryService(user_admin).create(ProductCategoryCreateScheme(**{
        'company_id': companies[1].id.__str__(),
        'title': 'Some Category 2'
    }))
    yield [product_category1, product_category2]
    await db_session.delete(product_category1)
    await db_session.delete(product_category2)
    await db_session.commit()

@pytest_asyncio.fixture
async def product_storage_types(db_session: AsyncSession, user_admin, companies) -> Company:
    product_storage_type1 = await ProductStorageTypeService(user_admin).create(ProductStorageTypeCreateScheme(**{
        'company_id': companies[0].id.__str__(),
        'title': 'Product Storage Type 1'
    }))
    product_storage_type2 = await ProductStorageTypeService(user_admin).create(ProductStorageTypeCreateScheme(**{
        'company_id': companies[1].id.__str__(),
        'title': 'Product Storage Type 2'
    }))
    yield [product_storage_type1, product_storage_type2]
    await db_session.delete(product_storage_type1)
    await db_session.delete(product_storage_type2)
    await db_session.commit()

@pytest_asyncio.fixture
async def uom_categories(db_session: AsyncSession, user_admin, companies) -> Company:
    uom_category1 = await UomCategoryService(user_admin).create(UomCategoryCreateScheme(**{
        'company_id': companies[0].id.__str__(),
        'title': 'Uom category 1'
    }))
    uom_category2 = await UomCategoryService(user_admin).create(UomCategoryCreateScheme(**{
        'company_id': companies[1].id.__str__(),
        'title': 'Uom category 2'
    }))
    yield [uom_category1, uom_category2]
    await db_session.delete(uom_category1)
    await db_session.delete(uom_category2)
    await db_session.commit()

@pytest_asyncio.fixture
async def uoms(db_session: AsyncSession, user_admin, companies, uom_categories) -> Company:
    uom1 = await UomService(user_admin).create(UomCreateScheme(**{
        'company_id': companies[0].id.__str__(),
        'title': 'ST',
        'category_id': uom_categories[0].id.__str__(),
        'type': UomType.STANDART,
        'ratio': 1,
        'precision': 1
    }))
    uom2 = await UomService(user_admin).create(UomCreateScheme(**{
        'company_id': companies[0].id.__str__(),
        'title': 'PAK10',
        'category_id': uom_categories[0].id.__str__(),
        'type': UomType.BIGGER,
        'ratio': 12,
        'precision': 0.5
    }))
    yield [uom1, uom2]
    await db_session.delete(uom1)
    await db_session.delete(uom2)
    await db_session.commit()

@pytest_asyncio.fixture
async def products(db_session: AsyncSession, user_admin, companies, uoms, product_storage_types, product_categories) -> Company:
    product1 = await ProductService(user_admin).create(ProductCreateScheme(**{
        'company_id': companies[0].id.__str__(),
        'title': 'Product 1',
        'description': 'Product Desc 1',
        'external_id': 'Product 1',
        'product_type': ProductType.STORABLE,
        'uom_id': uoms[0].id.__str__(),
        'product_category_id': product_categories[0].id.__str__(),
        'product_storage_type_id': product_storage_types[0].id.__str__(),
        'barcodes': ['Product1 Barcode1', 'Product1 Barcode2'],
    }))
    product2 = await ProductService(user_admin).create(ProductCreateScheme(**{
        'company_id': companies[1].id.__str__(),
        'title': 'Product 1',
        'description': 'Product 2',
        'external_id': 'Product 2',
        'product_type': ProductType.STORABLE,
        'uom_id': uoms[1].id.__str__(),
        'product_category_id': product_categories[1].id.__str__(),
        'product_storage_type_id': product_storage_types[1].id.__str__(),
        'barcodes': ['Product2 Barcode1', 'Product2 Barcode2'],
    }))
    yield [product1, product2]
    await db_session.delete(product1)
    await db_session.delete(product2)
    await db_session.commit()


@pytest_asyncio.fixture
async def location_types(db_session: AsyncSession, user_admin, companies) -> Company:
    location_type_partner = await LocationTypeService(user_admin).create(LocationTypeCreateScheme(**{
        'company_id': companies[0].id.__str__(),
        'title': 'PARTNER',
        'location_class': LocationClass.PARTNER
    }))
    location_type_place = await LocationTypeService(user_admin).create(LocationTypeCreateScheme(**{
        'company_id': companies[0].id.__str__(),
        'title': 'PLACE',
        'location_class': LocationClass.PLACE
    }))
    location_type_resource = await LocationTypeService(user_admin).create(LocationTypeCreateScheme(**{
        'company_id': companies[0].id.__str__(),
        'title': 'RESOURCE',
        'location_class': LocationClass.RESOURCE
    }))
    location_type_package = await LocationTypeService(user_admin).create(LocationTypeCreateScheme(**{
        'company_id': companies[0].id.__str__(),
        'title': 'PACKAGE',
        'location_class': LocationClass.PACKAGE
    }))
    location_type_zone = await LocationTypeService(user_admin).create(LocationTypeCreateScheme(**{
        'company_id': companies[0].id.__str__(),
        'title': 'ZONE',
        'location_class': LocationClass.ZONE
    }))
    location_type_lost = await LocationTypeService(user_admin).create(LocationTypeCreateScheme(**{
        'company_id': companies[0].id.__str__(),
        'title': 'LOST',
        'location_class': LocationClass.LOST
    }))
    location_type_inventory = await LocationTypeService(user_admin).create(LocationTypeCreateScheme(**{
        'company_id': companies[0].id.__str__(),
        'title': 'INVENTORY',
        'location_class': LocationClass.INVENTORY
    }))
    location_type_scrap = await LocationTypeService(user_admin).create(LocationTypeCreateScheme(**{
        'company_id': companies[0].id.__str__(),
        'title': 'SCRAP',
        'location_class': LocationClass.SCRAP
    }))
    location_type_scrapped = await LocationTypeService(user_admin).create(LocationTypeCreateScheme(**{
        'company_id': companies[0].id.__str__(),
        'title': 'SCRAPPED',
        'location_class': LocationClass.SCRAPPED
    }))
    location_type_buffer = await LocationTypeService(user_admin).create(LocationTypeCreateScheme(**{
        'company_id': companies[0].id.__str__(),
        'title': 'BUFFER',
        'location_class': LocationClass.BUFFER
    }))
    yield {
        'partner': location_type_partner,
        'place': location_type_place,
        'resource': location_type_resource,
        'package': location_type_package,
        'zone': location_type_zone,
        'lost': location_type_lost,
        'inventory': location_type_inventory,
        'scrap': location_type_scrap,
        'scrapped': location_type_scrapped,
        'buffer': location_type_buffer
    }
    await db_session.delete(location_type_partner)
    await db_session.delete(location_type_place)
    await db_session.delete(location_type_resource)
    await db_session.delete(location_type_package)
    await db_session.delete(location_type_zone)
    await db_session.delete(location_type_lost)
    await db_session.delete(location_type_inventory)
    await db_session.delete(location_type_scrap)
    await db_session.delete(location_type_scrapped)
    await db_session.delete(location_type_buffer)
    await db_session.commit()


@pytest_asyncio.fixture
async def locations(db_session: AsyncSession, user_admin, companies, stores, location_types, product_storage_types) -> dict:
    location_partner = await LocationService(user_admin).create(LocationCreateScheme(**{
        'company_id': companies[0].id.__str__(),
        'title': 'PARTNER',
        'store_id': stores[0].id.__str__(),
        #'parent_id': 'PARTNER',
        'active': True,
        'location_type_id': location_types['partner'].id.__str__(),
        'product_storage_type_ids': [i.id.__str__() for i in product_storage_types],
        #'partner_id': 'PARTNER',
        'homogeneity': False,
        'allow_create_package': True,
        'allowed_package_ids': [],
        'exclusive_package_ids': [],
        'allowed_order_types_ids': [],
        'exclusive_order_types_ids': [],
        'strategy': PutawayStrategy.FEFO

    }))
    location_place = await LocationService(user_admin).create(LocationCreateScheme(**{
        'company_id': companies[0].id.__str__(),
        'title': 'PLACE',
        'store_id': stores[0].id.__str__(),
        # 'parent_id': 'PARTNER',
        'active': True,
        'location_type_id': location_types['place'].id.__str__(),
        'product_storage_type_ids': [i.id.__str__() for i in product_storage_types],
        # 'partner_id': 'PARTNER',
        'homogeneity': False,
        'allow_create_package': True,
        'allowed_package_ids': [],
        'exclusive_package_ids': [],
        'allowed_order_types_ids': [],
        'exclusive_order_types_ids': [],
        'strategy': PutawayStrategy.FEFO
    }))
    location_resource = await LocationService(user_admin).create(LocationCreateScheme(**{
        'company_id': companies[0].id.__str__(),
        'title': 'RESOURCE',
        'store_id': stores[0].id.__str__(),
        # 'parent_id': 'PARTNER',
        'active': True,
        'location_type_id': location_types['resource'].id.__str__(),
        'product_storage_type_ids': [i.id.__str__() for i in product_storage_types],
        # 'partner_id': 'PARTNER',
        'homogeneity': False,
        'allow_create_package': True,
        'allowed_package_ids': [],
        'exclusive_package_ids': [],
        'allowed_order_types_ids': [],
        'exclusive_order_types_ids': [],
        'strategy': PutawayStrategy.FEFO
    }))
    location_package = await LocationService(user_admin).create(LocationCreateScheme(**{
        'company_id': companies[0].id.__str__(),
        'title': 'PACKAGE',
        'store_id': stores[0].id.__str__(),
        # 'parent_id': 'PARTNER',
        'active': True,
        'location_type_id': location_types['package'].id.__str__(),
        'product_storage_type_ids': [i.id.__str__() for i in product_storage_types],
        # 'partner_id': 'PARTNER',
        'homogeneity': False,
        'allow_create_package': True,
        'allowed_package_ids': [],
        'exclusive_package_ids': [],
        'allowed_order_types_ids': [],
        'exclusive_order_types_ids': [],
        'strategy': PutawayStrategy.FEFO
    }))
    location_zone = await LocationService(user_admin).create(LocationCreateScheme(**{
        'company_id': companies[0].id.__str__(),
        'title': 'ZONE',
        'store_id': stores[0].id.__str__(),
        # 'parent_id': 'PARTNER',
        'active': True,
        'location_type_id': location_types['zone'].id.__str__(),
        'product_storage_type_ids': [i.id.__str__() for i in product_storage_types],
        # 'partner_id': 'PARTNER',
        'homogeneity': False,
        'allow_create_package': True,
        'allowed_package_ids': [],
        'exclusive_package_ids': [],
        'allowed_order_types_ids': [],
        'exclusive_order_types_ids': [],
        'strategy': PutawayStrategy.FEFO
    }))
    location_lost = await LocationService(user_admin).create(LocationCreateScheme(**{
        'company_id': companies[0].id.__str__(),
        'title': 'LOST',
        'store_id': stores[0].id.__str__(),
        # 'parent_id': 'PARTNER',
        'active': True,
        'location_type_id': location_types['lost'].id.__str__(),
        'product_storage_type_ids': [i.id.__str__() for i in product_storage_types],
        # 'partner_id': 'PARTNER',
        'homogeneity': False,
        'allow_create_package': True,
        'allowed_package_ids': [],
        'exclusive_package_ids': [],
        'allowed_order_types_ids': [],
        'exclusive_order_types_ids': [],
        'strategy': PutawayStrategy.FEFO
    }))
    location_inventory = await LocationService(user_admin).create(LocationCreateScheme(**{
        'company_id': companies[0].id.__str__(),
        'title': 'LOST',
        'store_id': stores[0].id.__str__(),
        # 'parent_id': 'PARTNER',
        'active': True,
        'location_type_id': location_types['inventory'].id.__str__(),
        'product_storage_type_ids': [i.id.__str__() for i in product_storage_types],
        # 'partner_id': 'PARTNER',
        'homogeneity': False,
        'allow_create_package': True,
        'allowed_package_ids': [],
        'exclusive_package_ids': [],
        'allowed_order_types_ids': [],
        'exclusive_order_types_ids': [],
        'strategy': PutawayStrategy.FEFO
    }))
    location_scrap = await LocationService(user_admin).create(LocationCreateScheme(**{
        'company_id': companies[0].id.__str__(),
        'title': 'SCRAP',
        'store_id': stores[0].id.__str__(),
        # 'parent_id': 'PARTNER',
        'active': True,
        'location_type_id': location_types['scrap'].id.__str__(),
        'product_storage_type_ids': [i.id.__str__() for i in product_storage_types],
        # 'partner_id': 'PARTNER',
        'homogeneity': False,
        'allow_create_package': True,
        'allowed_package_ids': [],
        'exclusive_package_ids': [],
        'allowed_order_types_ids': [],
        'exclusive_order_types_ids': [],
        'strategy': PutawayStrategy.FEFO
    }))
    location_scrapped = await LocationService(user_admin).create(LocationCreateScheme(**{
        'company_id': companies[0].id.__str__(),
        'title': 'SCRAPPED',
        'store_id': stores[0].id.__str__(),
        # 'parent_id': 'PARTNER',
        'active': True,
        'location_type_id': location_types['scrapped'].id.__str__(),
        'product_storage_type_ids': [i.id.__str__() for i in product_storage_types],
        # 'partner_id': 'PARTNER',
        'homogeneity': False,
        'allow_create_package': True,
        'allowed_package_ids': [],
        'exclusive_package_ids': [],
        'allowed_order_types_ids': [],
        'exclusive_order_types_ids': [],
        'strategy': PutawayStrategy.FEFO
    }))
    location_buffer = await LocationService(user_admin).create(LocationCreateScheme(**{
        'company_id': companies[0].id.__str__(),
        'title': 'SCRAPPED',
        'store_id': stores[0].id.__str__(),
        # 'parent_id': 'PARTNER',
        'active': True,
        'location_type_id': location_types['buffer'].id.__str__(),
        'product_storage_type_ids': [i.id.__str__() for i in product_storage_types],
        # 'partner_id': 'PARTNER',
        'homogeneity': False,
        'allow_create_package': True,
        'allowed_package_ids': [],
        'exclusive_package_ids': [],
        'allowed_order_types_ids': [],
        'exclusive_order_types_ids': [],
        'strategy': PutawayStrategy.FEFO
    }))
    yield {
        'partner': location_partner,
        'place': location_place,
        'resource': location_resource,
        'package': location_package,
        'zone': location_zone,
        'lost': location_lost,
        'inventory': location_inventory,
        'scrap': location_scrap,
        'scrapped': location_scrapped,
        'buffer': location_buffer
    }
    await db_session.delete(location_partner)
    await db_session.delete(location_place)
    await db_session.delete(location_resource)
    await db_session.delete(location_package)
    await db_session.delete(location_zone)
    await db_session.delete(location_lost)
    await db_session.delete(location_inventory)
    await db_session.delete(location_scrap)
    await db_session.delete(location_scrapped)
    await db_session.delete(location_buffer)
    await db_session.commit()

@pytest_asyncio.fixture
async def lots(db_session: AsyncSession, user_admin, companies, products) -> Company:
    lot1 = await LotService(user_admin).create(LotCreateScheme(**{
        'company_id': companies[0].id.__str__(),
        'expiration_date': datetime.now().isoformat(),
        'product_id': products[0].id.__str__(),
        'external_id': '1000001',
    }))
    lot2 = await LotService(user_admin).create(LotCreateScheme(**{
        'company_id': companies[0].id.__str__(),
        'expiration_date': datetime.now().isoformat(),
        'product_id': products[0].id.__str__(),
        'external_id': '1000002',
    }))
    yield [lot1, lot2]
    await db_session.delete(lot1)
    await db_session.delete(lot2)
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
        "locale": "EN",
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
        "locale": "RU",
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
async def test_health(async_client, headers, stores, product_categories, product_storage_types, uom_categories, uoms, products, locations):
    response = await async_client.get("/api/fundamental/health", headers=headers['superadmin'])
    assert response.status_code == 200
