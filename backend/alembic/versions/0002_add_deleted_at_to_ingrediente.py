"""add_deleted_at_to_ingrediente

Revision ID: 0002_add_deleted_at_to_ingrediente
Revises: 8870fc96cf0d
Create Date: 2026-05-11 00:00:00.000000

"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0002_deleted_at_ingred'
down_revision = '8870fc96cf0d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'ingrediente',
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column('ingrediente', 'deleted_at')
