"""alterar coluna

Revision ID: 1d49bb956f39
Revises: 31844629f7c9
Create Date: 2026-04-05 11:06:07.150096

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '1d49bb956f39'
down_revision = '31844629f7c9'
branch_labels = None
depends_on = None


def upgrade():
    # Em vez de tentar converter (cast), removemos e recriamos a coluna
    # Isso é seguro pois você confirmou que a tabela está vazia
    with op.batch_alter_table('plans', schema=None) as batch_op:
        batch_op.drop_column('features')
        batch_op.add_column(sa.Column('features', sa.ARRAY(sa.String()), nullable=False, server_default='{}'))

def downgrade():
    with op.batch_alter_table('plans', schema=None) as batch_op:
        batch_op.drop_column('features')
        batch_op.add_column(sa.Column('features', postgresql.JSONB(astext_type=sa.Text()), nullable=False))