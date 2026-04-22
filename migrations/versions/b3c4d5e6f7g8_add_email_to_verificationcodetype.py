"""add EMAIL to verificationcodetype enum

Revision ID: b3c4d5e6f7g8
Revises: a1b2c3d4e5f6
Create Date: 2026-04-22 17:40:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b3c4d5e6f7g8'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade():
    # Add EMAIL to existing enum type verificationcodetype
    op.execute("ALTER TYPE verificationcodetype ADD VALUE 'EMAIL'")


def downgrade():
    # Downgrade not implemented: removing enum labels in Postgres is non-trivial
    pass
