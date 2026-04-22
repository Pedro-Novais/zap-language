"""corrigindo heads duplicados

Revision ID: 93d68cc6a19d
Revises: 2f7e1b4c9d12, a1b2c3d4e5f6
Create Date: 2026-04-22 13:34:12.326799

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '93d68cc6a19d'
down_revision = ('2f7e1b4c9d12', 'a1b2c3d4e5f6')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
