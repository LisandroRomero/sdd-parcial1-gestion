"""add composite index on pedido(usuario_id, created_at) for list pagination

Revision ID: 0005_add_composite_idx
Revises: 0004_add_fields
Create Date: 2026-05-14 00:00:00.000000
"""
from __future__ import annotations
from alembic import op

revision = '0005_add_composite_idx'
down_revision = '0004_add_fields'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        'ix_pedido_usuario_id_created_at',
        'pedido',
        ['usuario_id', 'created_at'],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index('ix_pedido_usuario_id_created_at', table_name='pedido')
