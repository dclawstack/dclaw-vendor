"""vendor directory: classification + enrichment columns (Phase 3)

Revision ID: a3c1d9f2b7e4
Revises: fb49db08f9a6
Create Date: 2026-05-30 09:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'a3c1d9f2b7e4'
down_revision: Union[str, None] = 'fb49db08f9a6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('vendors', sa.Column('category', sa.String(length=120), nullable=True))
    op.add_column('vendors', sa.Column('industry', sa.String(length=120), nullable=True))
    op.add_column(
        'vendors',
        sa.Column(
            'tier',
            sa.Enum(
                'strategic', 'preferred', 'approved', 'transactional',
                name='vendortier', native_enum=False, length=20,
            ),
            nullable=True,
        ),
    )
    op.add_column('vendors', sa.Column('website', sa.String(length=255), nullable=True))
    op.add_column('vendors', sa.Column('enrichment', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.create_index(op.f('ix_vendors_category'), 'vendors', ['category'], unique=False)
    op.create_index(op.f('ix_vendors_industry'), 'vendors', ['industry'], unique=False)
    op.create_index(op.f('ix_vendors_tier'), 'vendors', ['tier'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_vendors_tier'), table_name='vendors')
    op.drop_index(op.f('ix_vendors_industry'), table_name='vendors')
    op.drop_index(op.f('ix_vendors_category'), table_name='vendors')
    op.drop_column('vendors', 'enrichment')
    op.drop_column('vendors', 'website')
    op.drop_column('vendors', 'tier')
    op.drop_column('vendors', 'industry')
    op.drop_column('vendors', 'category')
