"""Agrega role a UserBoard

Revision ID: 3240324182a4
Revises: 67fac1e8fdd7
Create Date: 2025-09-11 12:26:36.358070

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3240324182a4'
down_revision = '67fac1e8fdd7'
branch_labels = None
depends_on = None


def upgrade():
    # 1. Crea el tipo ENUM en PostgreSQL
    board_role = sa.Enum('OWNER', 'ADMIN', 'MEMBER', name='board_role')
    board_role.create(op.get_bind(), checkfirst=True)
    # 2. Ahora agrega la columna usando ese tipo
    op.add_column('user_board', sa.Column('role', board_role, nullable=False, server_default='MEMBER'))

def downgrade():
    op.drop_column('user_board', 'role')
    sa.Enum(name='board_role').drop(op.get_bind(), checkfirst=True)
