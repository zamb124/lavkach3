"""create_initials_objects

Revision ID: 6ea1b38aba41
Revises: 56cec5ccc052
Create Date: 2023-06-30 22:49:14.306848

"""
from alembic import op
import sqlalchemy as sa
from uuid import uuid4
from app.basic.company.models.company_models import Company
from app.basic.user.models.user_models import User
from app.basic.user.models.role_models import Role
from app.basic.store.models.store_models import Store
from datetime import datetime
from sqlalchemy_utils.types import PasswordType

# revision identifiers, used by Alembic.
revision = '6ea1b38aba41'
down_revision = 'f9e0bfba8d29'
branch_labels = None
depends_on = 'f9e0bfba8d29'


def upgrade():
    company_1_id = uuid4().__str__()
    company_2_id = uuid4().__str__()
    store_1_company_1_id = uuid4().__str__()
    store_2_company_1_id = uuid4().__str__()
    store_3_company_1_id = uuid4().__str__()
    store_1_company_2_id = uuid4().__str__()
    store_2_company_2_id = uuid4().__str__()
    store_3_company_2_id = uuid4().__str__()
    user_admin_id = uuid4().__str__()
    user_1_company_1_id = uuid4().__str__()
    user_2_company_1_id = uuid4().__str__()
    user_1_company_2_id = uuid4().__str__()
    user_2_company_2_id = uuid4().__str__()
    role_1_company_1_id = uuid4().__str__()
    role_2_company_1_id = uuid4().__str__()
    role_1_company_2_id = uuid4().__str__()
    role_2_company_2_id = uuid4().__str__()
    from passlib.hash import pbkdf2_sha512
    target = User()
    target.password = '1402'
    new_password = pbkdf2_sha512.encrypt("1402")

    # ### commands auto generated by Alembic - please adjust! ###
    op.bulk_insert(Company.__table__,
                   [
                       {
                           'id': company_1_id,
                           'lsn': 1,
                           "title": "Apple",
                           "external_id": "100000",
                           "locale": "en_US",
                           "country": "US",
                           "currency": "USD",
                           'created_at': datetime.now(),
                           'updated_at': datetime.now(),
                       },
                       {
                           'id': company_2_id,
                           'lsn': 2,
                           "title": "Yandex",
                           "external_id": "100001",
                           "locale": "ru_RU",
                           "country": "RU",
                           "currency": "RUB",
                           'created_at': datetime.now(),
                           'updated_at': datetime.now(),
                       }
                   ])
    op.bulk_insert(Store.__table__,
                   [
                       {
                           'id': store_1_company_1_id,
                           'lsn': 1,
                           "company_id": company_1_id,
                           "title": "Apple Store New York",
                           "external_id": "100",
                           "address": "Gansevoort St",
                           "source": "internal",
                           'created_at': datetime.now(),
                           'updated_at': datetime.now(),
                       },
                       {
                           'id': store_2_company_1_id,
                           'lsn': 2,
                           "company_id": company_1_id,
                           "title": "Apple Store Florida",
                           "external_id": "101",
                           "address": "Florida St",
                           "source": "internal",
                           'created_at': datetime.now(),
                           'updated_at': datetime.now(),
                       },
                       {
                           'id': store_3_company_1_id,
                           'lsn': 2,
                           "company_id": company_1_id,
                           "title": "Apple Store Denver",
                           "external_id": "109",
                           "address": "Denver St",
                           "source": "internal",
                           'created_at': datetime.now(),
                           'updated_at': datetime.now(),
                       },
                       {
                           'id': store_1_company_2_id,
                           'lsn': 1,
                           "company_id": company_2_id,
                           "title": "Yandex Market",
                           "external_id": "117",
                           "address": "Lenina 4",
                           "source": "internal",
                           'created_at': datetime.now(),
                           'updated_at': datetime.now(),
                       },
                       {
                           'id': store_2_company_2_id,
                           'lsn': 2,
                           "company_id": company_2_id,
                           "title": "Yandex HUB Taxi",
                           "external_id": "108",
                           "address": "Stalina 90 st",
                           "source": "internal",
                           'created_at': datetime.now(),
                           'updated_at': datetime.now(),
                       },
                       {
                           'id': store_3_company_2_id,
                           'lsn': 2,
                           "company_id": company_2_id,
                           "title": "Yandex Lavka Gamovniki",
                           "external_id": "102",
                           "address": "Burjuya 17 St",
                           "source": "internal",
                           'created_at': datetime.now(),
                           'updated_at': datetime.now(),
                       }
                   ])

    op.bulk_insert(Role.__table__,
                   [
                       {
                           "id": role_1_company_1_id,
                           'lsn': 2,
                           "title": "support",
                           'created_at': datetime.now(),
                           'updated_at': datetime.now(),
                           "permissions_allow": [
                               "user_create",
                               "user_edit",
                               "user_list",
                               "user_delete",
                               "user_get",
                           ],
                           "company_id": company_1_id
                       },
                       {
                           "id": role_2_company_1_id,
                           "title": "admin",
                           'lsn': 3,
                           'created_at': datetime.now(),
                           'updated_at': datetime.now(),
                           "permissions_allow": [
                               "company_create",
                               "company_edit",
                               "company_list",
                               "company_delete",
                               "company_get",
                           ],
                           "company_id": company_1_id
                       },
                       {
                           "id": role_1_company_2_id,
                           'lsn': 4,
                           "title": "support",
                           'created_at': datetime.now(),
                           'updated_at': datetime.now(),
                           "permissions_allow": [
                               "user_create",
                               "user_edit",
                               "user_list",
                               "user_delete",
                               "user_get",
                           ],
                           "company_id": company_2_id
                       },
                       {
                           "id": role_2_company_2_id,
                           'lsn': 5,
                           "title": "admin",
                           'created_at': datetime.now(),
                           'updated_at': datetime.now(),
                           "permissions_allow": [
                               "company_create",
                               "company_edit",
                               "company_list",
                               "company_delete",
                               "company_get",
                           ],
                           "company_id": company_2_id
                       }
                   ])
    op.bulk_insert(User.__table__,
                   [
                       {
                           "id": user_admin_id,
                           'lsn': 1,
                           "email": "admin@admin.ru",
                           "country": "US",
                           "locale": "en_US",
                           "phone_number": "+449534771093",
                           "nickname": "Admin",
                           "is_admin": True,
                           'created_at': datetime.now(),
                           'updated_at': datetime.now(),
                           "password": '1402'
                       },
                       {
                           "id": user_1_company_1_id,
                           'lsn': 3,
                           "email": "user1@apple.ru",
                           "country": "RU",
                           "locale": "ru_RU",
                           "phone_number": "+449534771093",
                           "nickname": "Albert",
                           'created_at': datetime.now(),
                           'updated_at': datetime.now(),
                           "roles": [
                               role_1_company_1_id
                           ],
                           "is_admin": False,
                           "password": '1402'
                       },
                       {
                           "id": user_2_company_1_id,
                           'lsn': 4,
                           "email": "user2@apple.ru",
                           "country": "RU",
                           "locale": "ru_RU",
                           "phone_number": "+449534771093",
                           "nickname": "Albert",
                           'created_at': datetime.now(),
                           'updated_at': datetime.now(),
                           "roles": [
                               role_2_company_1_id
                           ],
                           "is_admin": False,
                           "password": '1402'
                       },
                       {
                           "id": user_1_company_2_id,
                           'lsn': 5,
                           "email": "user1@yandex.ru",
                           "country": "RU",
                           "locale": "ru_RU",
                           "phone_number": "+449534771093",
                           "nickname": "Albert",
                           'created_at': datetime.now(),
                           'updated_at': datetime.now(),
                           "is_admin": False,
                           "roles": [
                               role_1_company_2_id
                           ],
                           "password": '1402'
                       },
                       {
                           "id": user_2_company_2_id,
                           'lsn': 6,
                           "email": "user2@yandex.ru",
                           "country": "RU",
                           "locale": "ru_RU",
                           "phone_number": "+449534771093",
                           "nickname": "Albert",
                           "is_admin": False,
                           'created_at': datetime.now(),
                           'updated_at': datetime.now(),
                           "roles": [
                               role_2_company_2_id
                           ],
                           "password": '1402'
                       }
                   ])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute(f"TRUNCATE TABLE {Company.__tablename__}")
    op.execute(f"TRUNCATE TABLE {Store.__tablename__}")
    op.execute(f"TRUNCATE TABLE {Role.__tablename__}")
    op.execute(f"TRUNCATE TABLE {User.__tablename__}")
