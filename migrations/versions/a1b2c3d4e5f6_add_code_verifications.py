"""rename phone_verifications to code_verifications and add code_type enum

Revision ID: a1b2c3d4e5f6
Revises: 91960a25b580
Create Date: 2026-04-22 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '91960a25b580'
branch_labels = None
depends_on = None


def upgrade():
    verification_enum = sa.Enum('PHONE', 'NUMBER', name='verificationcodetype')
    verification_enum.create(op.get_bind(), checkfirst=True)

    op.rename_table('phone_verifications', 'code_verifications')
    op.add_column(
        'code_verifications',
        sa.Column('code_type', verification_enum, nullable=False, server_default=sa.text("'PHONE'")),
    )

    op.alter_column(
        'code_verifications',
        'phone_number',
        existing_type=sa.String(),
        new_column_name='value',
    )


def downgrade():
    op.alter_column(
        'code_verifications',
        'value',
        existing_type=sa.String(),
        new_column_name='phone_number',
    )

    op.drop_column('code_verifications', 'code_type')

    op.rename_table('code_verifications', 'phone_verifications')

    verification_enum = sa.Enum('PHONE', 'NUMBER', name='verificationcodetype')
    verification_enum.drop(op.get_bind(), checkfirst=True)
