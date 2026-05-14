"""add activo column to formapago

Revision ID: 0006_add_activo_to_formapago
Revises: 0005_add_composite_idx
Create Date: 2026-05-14 07:00:00.000000
"""
from __future__ import annotations
from alembic import op
import sqlalchemy as sa

revision = '0006_add_activo_to_formapago'
down_revision = '0005_add_composite_idx'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('formapago', sa.Column('activo', sa.Boolean(), nullable=False, server_default='true'))


def downgrade() -> None:
    op.drop_column('formapago', 'activo')
