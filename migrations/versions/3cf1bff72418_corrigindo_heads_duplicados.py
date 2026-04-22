"""corrigindo heads duplicados

Revision ID: 3cf1bff72418
Revises: 93d68cc6a19d, b3c4d5e6f7g8
Create Date: 2026-04-22 14:36:27.914769

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3cf1bff72418'
down_revision = ('93d68cc6a19d', 'b3c4d5e6f7g8')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
