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

    op.execute("create sequence companies_lsn_seq")
    op.execute("create sequence contractors_lsn_seq")
    op.execute("create sequence stores_lsn_seq")
    op.execute("create sequence servicesuppliers_lsn_seq")
    op.execute("create sequence manufacturers_lsn_seq")
    op.execute("create sequence assettypes_lsn_seq")
    op.execute("create sequence models_lsn_seq")
    op.execute("create sequence assets_lsn_seq")

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # ### end Alembic commands ###
    op.execute("drop sequence companies_lsn_seq")
    op.execute("drop sequence contractors_lsn_seq")
    op.execute("drop sequence stores_lsn_seq")
    op.execute("drop sequence servicesuppliers_lsn_seq")
    op.execute("drop sequence manufacturers_lsn_seq")
    op.execute("drop sequence assettypes_lsn_seq")
    op.execute("drop sequence models_lsn_seq")
    op.execute("drop sequence assets_lsn_seq")