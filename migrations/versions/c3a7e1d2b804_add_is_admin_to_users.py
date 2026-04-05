"""add is_admin to users

Revision ID: c3a7e1d2b804
Revises: 31844629f7c9
Create Date: 2026-04-05 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'c3a7e1d2b804'
down_revision = '31844629f7c9'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('is_admin', sa.Boolean(), server_default=sa.text('false'), nullable=False)
        )


def downgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('is_admin')
