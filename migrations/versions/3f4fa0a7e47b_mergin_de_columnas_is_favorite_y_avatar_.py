"""Mergin de columnas is_favorite y avatar_url de la tabla user

Revision ID: 3f4fa0a7e47b
Revises: 6fbbb69d677d, bf313f91126f
Create Date: 2025-08-07 19:49:24.356617

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3f4fa0a7e47b'
down_revision = ('6fbbb69d677d', 'bf313f91126f')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
