"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


def upgrade():
    ${upgrades if upgrades else "pass"}
    op.execute("create sequence suggest_lsn_seq")
    op.execute("create sequence order_type_lsn_seq")
    op.execute("create sequence order_lsn_seq")
    op.execute("create sequence move_lsn_seq")
    op.execute("create sequence move_log_lsn_seq")
    op.execute("create sequence location_lsn_seq")
    op.execute("create sequence location_type_lsn_seq")
    op.execute("create sequence lot_lsn_seq")
    op.execute("create sequence product_storage_type_lsn_seq")
    op.execute("create sequence quant_lsn_seq")
    op.execute("create sequence channel_lsn_seq")
    op.execute("create sequence product_lsn_seq")
    op.execute("create sequence product_category_lsn_seq")
    op.execute("create sequence permission_lsn_seq")
    op.execute("create sequence role_lsn_seq")
    op.execute("create sequence partner_lsn_seq")
    op.execute("create sequence uom_lsn_seq")
    op.execute("create sequence uom_category_lsn_seq")
    op.execute("create sequence company_lsn_seq")
    op.execute("create sequence user_lsn_seq")
    op.execute("create sequence store_lsn_seq")
    op.execute("create sequence storage_type_lsn_seq")
    op.execute("create sequence bus_lsn_seq")

def downgrade():
    ${downgrades if downgrades else "pass"}
    op.execute("drop sequence suggest_lsn_seq")
    op.execute("drop sequence order_type_lsn_seq")
    op.execute("drop sequence order_lsn_seq")
    op.execute("drop sequence move_lsn_seq")
    op.execute("drop sequence move_log_lsn_seq")
    op.execute("drop sequence location_lsn_seq")
    op.execute("drop sequence location_type_lsn_seq")
    op.execute("drop sequence lot_lsn_seq")
    op.execute("drop sequence product_storage_type_lsn_seq")
    op.execute("drop sequence quant_lsn_seq")
    op.execute("drop sequence channel_lsn_seq")
    op.execute("drop sequence product_lsn_seq")
    op.execute("drop sequence product_category_lsn_seq")
    op.execute("drop sequence permission_lsn_seq")
    op.execute("drop sequence role_lsn_seq")
    op.execute("drop sequence partner_lsn_seq")
    op.execute("drop sequence uom_lsn_seq")
    op.execute("drop sequence uom_category_lsn_seq")
    op.execute("drop sequence company_lsn_seq")
    op.execute("drop sequence user_lsn_seq")
    op.execute("drop sequence contractor_lsn_seq")
    op.execute("drop sequence store_lsn_seq")
    op.execute("drop sequence storage_type_lsn_seq")
    op.execute("drop sequence bus_lsn_seq")