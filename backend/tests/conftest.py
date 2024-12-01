import asyncio
import logging
import os
from datetime import datetime
from typing import Any
from unittest.mock import patch
from uuid import uuid4
from core.types import custom_dumps  # ВАЖНАЯ ДИЧ
from app.inventory.product_storage import StorageTypeCreateScheme, ProductStorageTypeCreateScheme
from core.db_config import config
import pytest
import pytest_asyncio
from dotenv import load_dotenv
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine

from app.basic.basic_server import app as basic_app
from app.basic.product.models import ProductType
from app.basic.product.schemas import ProductCategoryCreateScheme, ProductCreateScheme
from app.basic.store.schemas import StoreCreateScheme
from app.basic.uom.models import UomType
from app.basic.uom.schemas import UomCategoryCreateScheme, UomCreateScheme
from app.front.front_server import app as front_app
from app.inventory.inventory_server import app as inventory_app
from app.inventory.location.enums import LocationClass
from app.inventory.location.schemas import LocationTypeCreateScheme, LocationCreateScheme
from app.inventory.order.schemas import OrderTypeCreateScheme
from app.inventory.quant.schemas import LotCreateScheme, QuantCreateScheme
from core.context import set_session_context, reset_session_context
from core.core_apps.base.base_server import app as base_app
from core.core_apps.base.company.models import Company
from core.core_apps.base.company.schemas import CompanyCreateScheme
from core.core_apps.base.user.models import User
from core.core_apps.base.user.schemas import UserCreateScheme, RoleCreateScheme
from core.core_apps.bus.bus_server import app as bus_app
from core.db.session import Base

from core.env import Env, env_context
from core.fastapi.schemas import CurrentUser
from core.helpers.broker import list_brocker  # noqa: F401, isort:skip
from core.permissions import permits
from core.utils.uom import calculate_quantity

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
session_id = str(uuid4())
context = set_session_context(session_id=session_id)


@pytest.fixture(scope='session', autouse=True)
def load_env():
    cwd = os.getcwd()
    env_path = os.path.join(cwd, os.environ.get('DOTENV_PATH') or '.env')
    load_dotenv(env_path)


@pytest.fixture(scope="session")
def event_loop(load_env) -> asyncio.AbstractEventLoop:
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def engine(event_loop):
    engine = create_async_engine(config.WRITER_DB_URL)
    yield engine
    engine.sync_engine.dispose()


@pytest_asyncio.fixture(scope="session")
async def prepare_db(engine):
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="session")
async def env(prepare_db) -> Env:
    async with env_context() as env:
        yield env
    reset_session_context(context=context)


@pytest_asyncio.fixture(scope="session")
async def basic_client(prepare_db, env: Env) -> AsyncClient:
    async with AsyncClient(app=basic_app, base_url="http://basic") as ac:
        yield ac


@pytest_asyncio.fixture(scope="session")
async def base_client(prepare_db, env: Env) -> AsyncClient:
    async with AsyncClient(app=base_app, base_url="http://base") as ac:
        yield ac


@pytest_asyncio.fixture(scope="session")
async def inventory_client(prepare_db, env: Env) -> AsyncClient:
    async with AsyncClient(app=inventory_app, base_url="http://inventory") as ac:
        yield ac


@pytest_asyncio.fixture(scope="session")
async def bus_client(prepare_db, env: Env) -> AsyncClient:
    async with AsyncClient(app=bus_app, base_url="http://bus") as ac:
        yield ac


@pytest_asyncio.fixture(scope="session")
async def front_client(prepare_db, env: Env) -> AsyncClient:
    async with AsyncClient(app=front_app, base_url="http://front") as ac:
        yield ac


@pytest_asyncio.fixture(scope="session")
async def user_admin(env: Env) -> User:
    user_admin = UserCreateScheme(**{
        "email": "admin@admin.com",
        "nickname": "admin",
        "locale": "RU",
        "is_admin": True,
        "password1": "1402",
        "password2": "1402"
    })
    user = env['user'].service
    user_db = await user.create(user_admin)
    admin_user = CurrentUser(
        user_id='a7b02056-4817-4309-aa08-79bf130ebae1',
        is_admin=True
    )
    env.request.user = admin_user

    yield admin_user
    await user.delete(user_db)
    await user.session.commit()




@pytest_asyncio.fixture(scope="session")
async def companies(env: Env, user_admin) -> Company:
    company = env['company'].service
    company1 = CompanyCreateScheme(title="Test company 1", currency='USD')
    company2 = CompanyCreateScheme(title="Test company 2", currency='RUB')
    company1_db = await company.create(company1)
    company2_db = await company.create(company2)
    yield [company1_db, company2_db]
    await company.delete(company1_db)
    await company.delete(company2_db)
    await company.session.commit()


@pytest_asyncio.fixture(scope="session")
async def stores(env: Env, user_admin, companies) -> Company:
    store = env['store'].service
    store1 = StoreCreateScheme(title="Store company 1", company_id=companies[0].id, address='addres 1')
    store2 = StoreCreateScheme(title="Store company 2", company_id=companies[1].id, address='addres 1')
    store1_db = await store.create(store1)
    store2_db = await store.create(store2)
    yield [store1_db, store2_db]
    await store.delete(store1_db)
    await store.delete(store2_db)
    await store.session.commit()


@pytest_asyncio.fixture(scope="session")
async def product_categories(env: Env, user_admin, companies) -> Company:
    product_category = env['product_category'].service
    product_category1 = await product_category.create(ProductCategoryCreateScheme(**{
        'company_id': companies[0].id.__str__(),
        'title': 'Some Category 1'
    }))
    product_category2 = await product_category.create(ProductCategoryCreateScheme(**{
        'company_id': companies[1].id.__str__(),
        'title': 'Some Category 2'
    }))
    yield [product_category1, product_category2]
    await product_category.delete(product_category1)
    await product_category.delete(product_category2)
    await product_category.session.commit()


@pytest_asyncio.fixture(scope="session")
async def uom_categories(env: Env, user_admin, companies) -> Company:
    uom_category = env['uom_category'].service
    uom_category1 = await uom_category.create(UomCategoryCreateScheme(**{
        'company_id': companies[0].id.__str__(),
        'title': 'Uom category 1'
    }))
    uom_category2 = await uom_category.create(UomCategoryCreateScheme(**{
        'company_id': companies[1].id.__str__(),
        'title': 'Uom category 2'
    }))
    yield [uom_category1, uom_category2]
    await uom_category.delete(uom_category1)
    await uom_category.delete(uom_category2)
    await uom_category.session.commit()


@pytest_asyncio.fixture(scope="session")
async def uoms(env: Env, user_admin, companies, uom_categories) -> Company:
    uom = env['uom'].service
    uom1 = await uom.create(UomCreateScheme(**{
        'company_id': companies[0].id.__str__(),
        'title': 'KG',
        'uom_category_id': uom_categories[0].id.__str__(),
        'type': UomType.STANDART,
        'ratio': 1,
        'precision': 0
    }))
    uom2 = await uom.create(UomCreateScheme(**{
        'company_id': companies[0].id.__str__(),
        'title': 'G',
        'uom_category_id': uom_categories[0].id.__str__(),
        'type': UomType.BIGGER,
        'ratio': 1000,
        'precision': 2
    }))
    yield [uom1, uom2]
    await uom.delete(uom1)
    await uom.delete(uom2)
    await uom.session.commit()


@pytest_asyncio.fixture(scope="session")
async def products(env: Env, user_admin, companies, uoms,
                   product_categories) -> Company:
    product = env['product'].service
    product1 = await product.create(ProductCreateScheme(**{
        'company_id': companies[0].id.__str__(),
        'title': 'Product 1',
        'description': 'Product Desc 1',
        'external_number': 'Product 1',
        'product_type': ProductType.STORABLE,
        'uom_id': uoms[0].id.__str__(),
        'product_category_id': product_categories[0].id.__str__(),
        'barcode_list': ['Product1 Barcode1', 'Product1 Barcode2'],
    }))
    product2 = await product.create(ProductCreateScheme(**{
        'company_id': companies[1].id.__str__(),
        'title': 'Product 1',
        'description': 'Product 2',
        'external_number': 'Product 2',
        'product_type': ProductType.STORABLE,
        'uom_id': uoms[1].id.__str__(),
        'product_category_id': product_categories[1].id.__str__(),
        'barcode_list': ['Product2 Barcode1', 'Product2 Barcode2'],
    }))
    yield [product1, product2]
    await product.delete(product1)
    await product.delete(product2)
    await product.session.commit()


@pytest_asyncio.fixture(scope="session")
async def location_types(env: Env, user_admin, companies) -> Company:
    location_type = env['location_type'].service
    location_type_package = await location_type.create(LocationTypeCreateScheme(**{
        'company_id': companies[0].id.__str__(),
        'title': 'PACKAGE',
        'location_class': LocationClass.PACKAGE
    }))
    location_type_partner = await location_type.create(LocationTypeCreateScheme(**{
        'company_id': companies[0].id.__str__(),
        'title': 'PARTNER',
        'location_class': LocationClass.PARTNER
    }))
    location_type_place = await location_type.create(LocationTypeCreateScheme(**{
        'company_id': companies[0].id.__str__(),
        'title': 'PLACE',
        'location_class': LocationClass.PLACE
    }))
    location_type_resource = await location_type.create(LocationTypeCreateScheme(**{
        'company_id': companies[0].id.__str__(),
        'title': 'RESOURCE',
        'location_class': LocationClass.RESOURCE
    }))

    location_type_zone = await location_type.create(LocationTypeCreateScheme(**{
        'company_id': companies[0].id.__str__(),
        'title': 'ZONE',
        'location_class': LocationClass.ZONE,
        'allowed_package_type_ids': [location_type_package.id]
    }))
    location_type_lost = await location_type.create(LocationTypeCreateScheme(**{
        'company_id': companies[0].id.__str__(),
        'title': 'LOST',
        'location_class': LocationClass.LOST
    }))
    location_type_inventory = await location_type.create(LocationTypeCreateScheme(**{
        'company_id': companies[0].id.__str__(),
        'title': 'INVENTORY',
        'location_class': LocationClass.INVENTORY
    }))
    location_type_scrap = await location_type.create(LocationTypeCreateScheme(**{
        'company_id': companies[0].id.__str__(),
        'title': 'SCRAP',
        'location_class': LocationClass.SCRAP
    }))
    location_type_scrapped = await location_type.create(LocationTypeCreateScheme(**{
        'company_id': companies[0].id.__str__(),
        'title': 'SCRAPPED',
        'location_class': LocationClass.SCRAPPED
    }))
    location_type_buffer = await location_type.create(LocationTypeCreateScheme(**{
        'company_id': companies[0].id.__str__(),
        'title': 'BUFFER',
        'location_class': LocationClass.PLACE,
        'allowed_package_type_ids': [location_type_package.id]
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
    await location_type.delete(location_type_partner)
    await location_type.delete(location_type_place)
    await location_type.delete(location_type_resource)
    await location_type.delete(location_type_package)
    await location_type.delete(location_type_zone)
    await location_type.delete(location_type_lost)
    await location_type.delete(location_type_inventory)
    await location_type.delete(location_type_scrap)
    await location_type.delete(location_type_scrapped)
    await location_type.delete(location_type_buffer)
    await location_type.session.commit()


@pytest_asyncio.fixture(scope="session")
async def locations(env: Env, user_admin, companies, stores, location_types) -> dict:
    location = env['location'].service
    location_type_service = env['location_type'].service
    location_partner = await location.create(LocationCreateScheme(**{
        'company_id': companies[0].id.__str__(),
        'title': 'PARTNER',
        'store_id': stores[0].id.__str__(),
        'location_class': LocationClass.PARTNER,
        'is_active': True,
        'location_type_id': location_types['partner'].id.__str__()
    }))

    location_resource = await location.create(LocationCreateScheme(**{
        'company_id': companies[0].id.__str__(),
        'title': 'RESOURCE',
        'store_id': stores[0].id.__str__(),
        'location_class': LocationClass.RESOURCE,
        'is_active': True,
        'location_type_id': location_types['resource'].id.__str__()
    }))

    location_zone = await location.create(LocationCreateScheme(**{
        'company_id': companies[0].id.__str__(),
        'title': 'MAIN ZONE',
        'store_id': stores[0].id.__str__(),
        'location_class': LocationClass.ZONE,
        'is_active': True,
        'location_type_id': location_types['zone'].id.__str__()
    }))

    location_place = await location.create(LocationCreateScheme(**{
        'company_id': companies[0].id,
        'title': 'PLACE',
        'location_id': location_zone.id,
        'store_id': stores[0].id,
        'location_class': LocationClass.PLACE,
        'is_active': True,
        'location_type_id': location_types['place'].id
    }))
    location_subzone = await location.create(LocationCreateScheme(**{
        'company_id': companies[0].id.__str__(),
        'title': 'SUBZONE',
        'store_id': stores[0].id.__str__(),
        'location_id': location_zone.id,
        'location_class': LocationClass.ZONE,
        'is_active': True,
        'location_type_id': location_types['zone'].id.__str__()
    }))
    location_subzone_place = await location.create(LocationCreateScheme(**{
        'company_id': companies[0].id,
        'title': 'SUBZONE PLACE',
        'location_id': location_subzone.id,
        'store_id': stores[0].id,
        'location_class': LocationClass.PLACE,
        'is_active': True,
        'location_type_id': location_types['place'].id
    }))
    location_package = await location.create(LocationCreateScheme(**{
        'company_id': companies[0].id,
        'title': 'PACKAGE',
        'store_id': stores[0].id,
        'location_id': location_zone.id,
        'location_class': LocationClass.PACKAGE,
        'is_active': True,
        'location_type_id': location_types['package'].id.__str__()
    }))
    location_lost = await location.create(LocationCreateScheme(**{
        'company_id': companies[0].id.__str__(),
        'title': 'LOST',
        'store_id': stores[0].id.__str__(),
        'location_class': LocationClass.LOST,
        'is_active': True,
        'location_type_id': location_types['lost'].id.__str__()
    }))
    location_inventory = await location.create(LocationCreateScheme(**{
        'company_id': companies[0].id.__str__(),
        'title': 'LOST',
        'store_id': stores[0].id.__str__(),
        'location_class': LocationClass.LOST,
        'is_active': True,
        'location_type_id': location_types['inventory'].id.__str__(),
    }))
    location_scrap = await location.create(LocationCreateScheme(**{
        'company_id': companies[0].id.__str__(),
        'title': 'SCRAP',
        'store_id': stores[0].id.__str__(),
        'location_class': LocationClass.SCRAP,
        'is_active': True,
        'location_type_id': location_types['scrap'].id.__str__(),

    }))
    location_scrapped = await location.create(LocationCreateScheme(**{
        'company_id': companies[0].id.__str__(),
        'title': 'SCRAPPED',
        'store_id': stores[0].id.__str__(),
        'location_class': LocationClass.SCRAPPED,
        'is_active': True,
        'location_type_id': location_types['scrapped'].id.__str__(),

    }))
    location_buffer = await location.create(LocationCreateScheme(**{
        'company_id': companies[0].id.__str__(),
        'title': 'INBOUND_BUFFER',
        'store_id': stores[0].id.__str__(),
        'location_class': LocationClass.ZONE,
        'is_active': True,
        'location_type_id': location_types['zone'].id.__str__(),

    }))
    yield {
        'partner': location_partner,
        'place': location_place,
        'resource': location_resource,
        'package': location_package,
        'zone': location_zone,
        'subzone': location_subzone,
        'subzone_place': location_subzone_place,
        'lost': location_lost,
        'inventory': location_inventory,
        'scrap': location_scrap,
        'scrapped': location_scrapped,
        'buffer': location_buffer
    }
    await location.delete(location_partner)
    await location.delete(location_place)
    await location.delete(location_resource)
    await location.delete(location_package)
    await location.delete(location_zone)
    await location.delete(location_lost)
    await location.delete(location_inventory)
    await location.delete(location_scrap)
    await location.delete(location_scrapped)
    await location.delete(location_buffer)
    await location.session.commit()


@pytest_asyncio.fixture(scope="session")
async def lots(env: Env, user_admin, companies, products) -> Company:
    lot = env['lot'].service
    lot1 = await lot.create(LotCreateScheme(**{
        'company_id': companies[0].id.__str__(),
        'expiration_datetime': datetime.now().isoformat(),
        'product_id': products[0].id.__str__(),
        'external_number': '1000001',
    }))
    lot2 = await lot.create(LotCreateScheme(**{
        'company_id': companies[0].id.__str__(),
        'expiration_datetime': datetime.now().isoformat(),
        'product_id': products[0].id.__str__(),
        'external_number': '1000002',
    }))
    yield [lot1, lot2]
    await lot.delete(lot1)
    await lot.delete(lot2)
    await lot.session.commit()


@pytest_asyncio.fixture(scope="session")
async def quants(env: Env, user_admin, companies, lots, products, stores, locations, uoms) -> Company:
    quant = env['quant'].service
    quant1 = await quant.create(QuantCreateScheme(**{
        'company_id': companies[0].id.__str__(),
        'product_id': products[0].id.__str__(),
        'store_id': stores[0].id.__str__(),
        'location_id': locations['place'].id.__str__(),
        'lot_id': lots[0].id.__str__(),
        'quantity': 10.0,
        'reserved_quantity': 5,
        'location_class': LocationClass.PLACE,
        'expiration_datetime': datetime.now().isoformat(),
        'uom_id': uoms[0].id.__str__()
    }))
    quant2 = await quant.create(QuantCreateScheme(**{
        'company_id': companies[0].id.__str__(),
        'product_id': products[0].id.__str__(),
        'store_id': stores[0].id.__str__(),
        'location_id': locations['zone'].id.__str__(),
        'lot_id': lots[1].id.__str__(),
        'quantity': 5,
        'reserved_quantity': 0,
        'location_class': LocationClass.PLACE,
        'expiration_datetime': datetime.now().isoformat(),
        'uom_id': uoms[0].id.__str__()
    }))
    quant3 = await quant.create(QuantCreateScheme(**{
        'company_id': companies[0].id,
        'product_id': products[0].id,
        'store_id': stores[0].id,
        'location_id': locations['zone'].id,
        'quantity': 15,
        'reserved_quantity': 0,
        'location_class': LocationClass.PLACE,
        'expiration_datetime': datetime.now().isoformat(),
        'uom_id': uoms[1].id
    }))
    quant4 = await quant.create(QuantCreateScheme(**{
        'company_id': companies[0].id,
        'product_id': products[0].id,
        'store_id': stores[0].id,
        'location_id': locations['zone'].id,
        'package_id': locations['package'].id,
        'quantity': 15,
        'reserved_quantity': 0,
        'location_class': LocationClass.PLACE,
        'expiration_datetime': datetime.now().isoformat(),
        'uom_id': uoms[0].id
    }))
    quant44 = await quant.create(QuantCreateScheme(**{
        'company_id': companies[0].id,
        'product_id': products[0].id,
        'store_id': stores[0].id,
        'location_id': locations['zone'].id,
        'package_id': locations['package'].id,
        'quantity': 10,
        'reserved_quantity': 0,
        'location_class': LocationClass.PLACE,
        'expiration_datetime': datetime.now().isoformat(),
        'uom_id': uoms[0].id
    }))
    quant5 = await quant.create(QuantCreateScheme(**{
        'company_id': companies[0].id,
        'product_id': products[0].id,
        'store_id': stores[0].id,
        'location_id': locations['subzone_place'].id,
        'quantity': 15,
        'reserved_quantity': 0,
        'location_class': LocationClass.PLACE,
        'expiration_datetime': datetime.now().isoformat(),
        'uom_id': uoms[0].id
    }))
    yield [quant1, quant2, quant3, quant4, quant44, quant5]
    await quant.delete(quant1)
    await quant.delete(quant2)
    await quant.delete(quant3)
    await quant.delete(quant4)
    await quant.delete(quant44)
    await quant.delete(quant5)
    await quant.session.commit()


@pytest_asyncio.fixture(scope="session")
async def order_types(env: Env, user_admin, companies, lots, products, stores, locations, uoms,
                      token, location_types) -> Company:
    order_type = env['order_type'].service
    inbound_order_type = await order_type.create(OrderTypeCreateScheme(**{
        'company_id': companies[0].id.__str__(),
        'prefix': 'IN',
        'title': 'Inbound Type',
        'order_class': 'incoming',
        'allowed_zone_ids': [locations['buffer'].id, ],
        'order_type_id': None,
        'backorder_action_type': 'ask',
        'store_id': None,
        'partner_id': None,
        'reservation_method': 'at_confirm',
        'reservation_time_before': 0,
        'is_homogeneity': False,
        'is_allow_create_package': True,
        'is_can_create_order_manualy': True,
        'is_overdelivery': False,
        'created_by': token['user_admin']['user_id'].__str__(),
        'edited_by': token['user_admin']['user_id'].__str__(),
        'barcode': '2132132131231',
        'strategy': 'fefo',
    }))
    lost_order_type = await order_type.create(OrderTypeCreateScheme(**{
        'company_id': companies[0].id.__str__(),
        'prefix': 'LO',
        'title': 'Lost Type',
        'order_class': 'incoming',
        'allowed_zone_ids': [locations['buffer'].id, locations['zone'].id, ],
        'order_type_id': None,
        'backorder_action_type': 'never',
        'store_id': None,
        'partner_id': None,
        'reservation_method': 'at_confirm',
        'reservation_time_before': 0,
        'is_homogeneity': False,
        'is_allow_create_package': False,
        'is_can_create_order_manualy': True,
        'is_overdelivery': False,
        'created_by': token['user_admin']['user_id'].__str__(),
        'edited_by': token['user_admin']['user_id'].__str__(),
        'barcode': '2132132131231',
        'strategy': 'fefo',
    }))
    placement_order_type = await order_type.create(OrderTypeCreateScheme(**{
        'company_id': companies[0].id.__str__(),
        'prefix': 'PL',
        'title': 'Placement Type',
        'order_class': 'internal',
        'allowed_zone_ids': [locations['zone'].id, locations['buffer'].id],
        'allowed_location_type_ids': [location_types['package'].id, location_types['zone'].id,
                                           location_types['place'].id, location_types['buffer'].id],
        'order_type_id': lost_order_type.id.__str__(),
        'backorder_action_type': 'always',
        'store_id': None,
        'partner_id': None,
        'reservation_method': 'at_confirm',
        'reservation_time_before': 0,
        'is_homogeneity': False,
        'is_allow_create_package': True,
        'is_can_create_order_manualy': True,
        'is_overdelivery': False,
        'created_by': token['user_admin']['user_id'].__str__(),
        'edited_by': token['user_admin']['user_id'].__str__(),
        'barcode': '2132132131231',
        'strategy': 'fefo',
    }))
    shipment_order_type = await order_type.create(OrderTypeCreateScheme(**{
        'company_id': companies[0].id.__str__(),
        'prefix': 'SH',
        'title': 'Shipment Type',
        'order_class': 'outgoing',
        'allowed_zone_ids': [locations['buffer'].id.__str__(), ],
        'order_type_id': None,
        'backorder_action_type': 'ask',
        'store_id': None,
        'partner_id': None,
        'reservation_method': 'at_confirm',
        'reservation_time_before': 0,
        'is_homogeneity': False,
        'is_allow_create_package': True,
        'is_can_create_order_manualy': True,
        'is_overdelivery': False,
        'created_by': token['user_admin']['user_id'].__str__(),
        'edited_by': token['user_admin']['user_id'].__str__(),
        'barcode': '2132132131231',
        'strategy': 'fefo',
    }))

    yield {
        'inbound': inbound_order_type,
        'placement': placement_order_type,
        'lost': lost_order_type,
        'shipment': shipment_order_type
    }
    await order_type.delete(inbound_order_type)
    await order_type.delete(placement_order_type)
    await order_type.delete(lost_order_type)
    await order_type.delete(shipment_order_type)
    await order_type.session.commit()


@pytest_asyncio.fixture(scope="session")
async def storage_types(env: Env, user_admin, companies, lots, products, stores, locations, uoms,
                        token, location_types) -> Company:
    storage_type_service = env['storage_type'].service
    storage_type = await storage_type_service.create(StorageTypeCreateScheme(**{
        'company_id': companies[0].id.__str__(),
        'title': 'Default Storage Type',
        'allowed_location_type_ids': [location_types['package'].id.__str__(), location_types['zone'].id.__str__()],
        'allowed_zones': [
            {'zone_id': locations['zone'].id, 'priority': 1},
            {'zone_id': locations['buffer'].id, 'priority': 2},
        ],
    }))

    yield {
        'default': storage_type,
    }
    await storage_type_service.delete(storage_type)


@pytest_asyncio.fixture(scope="session")
async def product_storage_types(env: Env, companies, storage_types, products, uoms, locations):
    product_storage_type_service = env['product_storage_type'].service
    product_storage_type_1 = await product_storage_type_service.create(ProductStorageTypeCreateScheme(**{
        'company_id': companies[0].id,
        'product_id': products[0].id,
        'storage_uom_id': uoms[0].id,
        'allowed_storage_uom_ids': [i.id for i in uoms],
        'allowed_package_type_ids': [locations['package'].id],
        'storage_type_id': storage_types['default'].id,
    }))
    yield {
        'product_storage_type_1': product_storage_type_1,
    }
    await product_storage_type_service.delete(product_storage_type_1)


@pytest_asyncio.fixture(scope="session")
async def roles(env: Env, companies, user_admin) -> User:
    role = env['role'].service
    permission_allow_list = [
        "user_create", 'user_edit', 'user_list', 'user_get', 'partner_create',
        'partner_edit', 'partner_list', 'partner_delete', 'partner_get',
        'company_create', 'company_edit', 'company_list', 'company_get',
        'uom_create', 'uom_edit', 'uom_list', 'uom_delete', 'uom_get']
    role_admin = RoleCreateScheme(title="admin", permission_allow_list=list(permits.keys()), company_id=companies[0].id)
    role_admin_db = await role.create(role_admin)
    role_support = RoleCreateScheme(title="support", permission_allow_list=permission_allow_list,
                                    company_id=companies[0].id,
                                    role_ids=[role_admin_db.id]
                                    )
    role_support_db = await role.create(role_support)
    yield {'admin': role_admin_db, 'support': role_support_db}
    await role.delete(role_admin_db)
    await role.delete(role_support_db)
    await role.session.commit()


@pytest_asyncio.fixture(scope="session")
async def users(env: Env, companies, roles, user_admin) -> User:
    user = env['user'].service
    company_admin = UserCreateScheme(**{
        "email": "company_admin@gmail.com",
        "nickname": "Admin vasya",
        "locale": "EN",
        "is_admin": False,
        "company_id": companies[0].id,
        "company_ids": [
            companies[0].id
        ],
        "role_ids": [
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
        "company_id": companies[0].id,
        "company_ids": [
            companies[0].id
        ],
        "role_ids": [
            roles.get('support').id
        ],
        "password1": "1402",
        "password2": "1402"
    })
    company_admin_db = await user.create(company_admin)
    company_support_db = await user.create(company_support)
    yield {'company_admin': company_admin_db, 'company_support': company_support_db}
    await user.delete(company_admin_db)
    await user.delete(company_support_db)
    await user.session.commit()


@pytest_asyncio.fixture(scope="session")
async def token(env: Env, users: User, user_admin) -> dict[str, Any]:
    user = env['user'].service
    user_admin = await user.login('admin@admin.com', '1402')
    company_admin = await user.login(users.get('company_admin').email, users.get('company_admin').password)
    company_support = await user.login(users.get('company_support').email,
                                       users.get('company_support').password)
    return {
        'user_admin': user_admin,
        'company_admin': company_admin,
        'company_support': company_support
    }


@pytest_asyncio.fixture(scope="session")
async def headers(token) -> dict:
    return {
        'superadmin': {'Authorization': token['user_admin']['token']},
        'company_admin': {'Authorization': token['company_admin']['token']},
        'company_support': {'Authorization': token['company_support']['token']}
    }


@pytest.mark.asyncio
async def test_health(base_client, headers, stores, product_categories, uom_categories, uoms, products, locations,
                      quants):
    response = await base_client.get("/api/base/health", headers=headers['superadmin'])
    assert response.status_code == 200

async def mock_convert(*args, **kwargs):
    payload = kwargs.get('payload')
    uoms = kwargs.get('uoms')
    result = []
    uoms_map = {uom.id: uom for uom in uoms}
    for pay in payload:
    # Используем данные из uoms и extra_param
        uom_in = uoms_map.get(pay.get('uom_id_in'))
        uom_out = uoms_map.get(pay.get('uom_id_out'))
        quantity_in = pay.get('quantity_in')
        quantity_out = calculate_quantity(
            uom_in_type=uom_in.type,
            uom_in_ratio=uom_in.ratio,
            uom_out_type=uom_out.type,
            uom_out_ratio=uom_out.ratio,
            uom_out_precision=uom_out.precision,
            quantity_in=quantity_in
        )
        result.append(
            {
                'quantity_out': quantity_out,
                'uom_id_out': uom_out.id,
                'quantity_in': quantity_in,
                'uom_id_in': uom_in.id,
            }
        )
    return result


@pytest_asyncio.fixture(scope="session")
def mock_uom_convert(uoms):
    extra_param = 'some_value'  # Пример значения для extra_param
    with patch('app.basic.basic_adapter.BasicAdapter.convert', lambda *args, **kwargs: mock_convert(*args, **kwargs, uoms=uoms, extra_param=extra_param)):
        yield