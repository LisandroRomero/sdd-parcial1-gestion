"""add_cantidad_unidad_to_producto_ingredientes

Revision ID: 0003_add_cantidad_unidad
Revises: 0002_deleted_at_ingred
Create Date: 2026-05-13 00:00:00.000000

"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0003_add_cantidad_unidad'
down_revision = '0002_deleted_at_ingred'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'productoingrediente',
        sa.Column('cantidad', sa.Float(), nullable=True),
    )
    op.add_column(
        'productoingrediente',
        sa.Column('unidad', sa.String(length=20), nullable=True),
    )


def downgrade() -> None:
    op.drop_column('productoingrediente', 'unidad')
    op.drop_column('productoingrediente', 'cantidad')
