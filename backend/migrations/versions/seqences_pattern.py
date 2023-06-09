"""initial

Revision ID: 1e8431842d98
Revises: 
Create Date: 2023-06-07 14:29:30.566708

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1e8431842d98'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.execute("create sequence bus_lsn_seq")
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
    op.execute("create sequence contractor_lsn_seq")
    op.execute("create sequence store_lsn_seq")
    op.execute("create sequence manufacturer_lsn_seq")
    op.execute("create sequence asset_type_lsn_seq")
    op.execute("create sequence model_lsn_seq")
    op.execute("create sequence asset_lsn_seq")

    op.execute("create sequence asset_log_lsn_seq")
    op.execute("create sequence order_lsn_seq")
    op.execute("create sequence order_number_seq")
    op.execute("create sequence order_line_lsn_seq")


    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # ### end Alembic commands ###
    op.execute("drop sequence channel_lsn_seq")
    op.execute("drop sequence bus_lsn_seq")
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
    op.execute("drop sequence service_supplier_lsn_seq")
    op.execute("drop sequence manufacturer_lsn_seq")
    op.execute("drop sequence asset_type_lsn_seq")
    op.execute("drop sequence model_lsn_seq")
    op.execute("drop sequence asset_lsn_seq")

    op.execute("drop sequence asset_log_lsn_seq")
    op.execute("drop sequence order_lsn_seq")
    op.execute("drop sequence order_number_seq")
    op.execute("drop sequence order_line_lsn_seq")