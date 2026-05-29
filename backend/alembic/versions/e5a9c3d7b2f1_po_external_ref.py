"""purchase_orders.external_ref for ERP sync (Phase 6, V6.4)

Revision ID: e5a9c3d7b2f1
Revises: d4f8a2c6e1b9
Create Date: 2026-05-30 13:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e5a9c3d7b2f1'
down_revision: Union[str, None] = 'd4f8a2c6e1b9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('purchase_orders', sa.Column('external_ref', sa.String(length=120), nullable=True))
    op.create_index(op.f('ix_purchase_orders_external_ref'), 'purchase_orders', ['external_ref'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_purchase_orders_external_ref'), table_name='purchase_orders')
    op.drop_column('purchase_orders', 'external_ref')
