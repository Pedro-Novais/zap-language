"""add payment customer id to users

Revision ID: e1f2d3c4b5a6
Revises: 60c4c6adc4fb
Create Date: 2026-05-05 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e1f2d3c4b5a6'
down_revision = '60c4c6adc4fb'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('payment_customer_id', sa.String(length=255), nullable=True),
        )
        batch_op.create_unique_constraint(
            'uq_users_payment_customer_id',
            ['payment_customer_id'],
        )


def downgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_constraint('uq_users_payment_customer_id', type_='unique')
        batch_op.drop_column('payment_customer_id'
        )
