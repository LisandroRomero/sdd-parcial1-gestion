"""add usuario_id and motivo to historialestadopedido

Revision ID: 0004_add_fields
Revises: f9f9bdb45616
Create Date: 2026-05-14 00:00:00.000000
"""
from __future__ import annotations
from alembic import op
import sqlalchemy as sa

revision = '0004_add_fields'
down_revision = 'f9f9bdb45616'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('historialestadopedido',
        sa.Column('usuario_id', sa.Integer(), nullable=True)
    )
    op.create_foreign_key(
        'fk_historialestadopedido_usuario',
        'historialestadopedido', 'usuario',
        ['usuario_id'], ['id']
    )
    op.add_column('historialestadopedido',
        sa.Column('motivo', sa.VARCHAR(255), nullable=True)
    )


def downgrade() -> None:
    op.drop_constraint('fk_historialestadopedido_usuario', 'historialestadopedido', type_='foreignkey')
    op.drop_column('historialestadopedido', 'usuario_id')
    op.drop_column('historialestadopedido', 'motivo')
