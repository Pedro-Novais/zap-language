"""Alterando tipo do campo role, na tabela message history

Revision ID: c5117272ee3a
Revises: 91960a25b580
Create Date: 2026-01-31 18:14:34.864576

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c5117272ee3a'
down_revision = '91960a25b580'
branch_labels = None
depends_on = None


def upgrade():
    # 1. Cria o tipo primeiro (você já fez isso corretamente)
    op.execute("CREATE TYPE messagerolemodel AS ENUM ('USER', 'ASSISTANT', 'SYSTEM')")
    
    with op.batch_alter_table('messages_history', schema=None) as batch_op:
        batch_op.alter_column('role',
               existing_type=sa.VARCHAR(length=20),
               # O SQLAlchemy usa type_ para definir o novo tipo
               type_=sa.Enum('USER', 'ASSISTANT', 'SYSTEM', name='messagerolemodel'),
               existing_nullable=False,
               # ESTA É A LINHA QUE RESOLVE O ERRO:
               postgresql_using='role::messagerolemodel') 

def downgrade():
    with op.batch_alter_table('messages_history', schema=None) as batch_op:
        batch_op.alter_column('role',
               existing_type=sa.Enum('USER', 'ASSISTANT', 'SYSTEM', name='messagerolemodel'),
               type_=sa.VARCHAR(length=20),
               existing_nullable=False)
               
    # Remove o tipo após a coluna voltar a ser VARCHAR
    op.execute("DROP TYPE messagerolemodel")