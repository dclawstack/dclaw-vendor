"""risk assessments + contracts (Phase 6, V6.1/V6.2)

Revision ID: d4f8a2c6e1b9
Revises: c9d3e6b1f8a2
Create Date: 2026-05-30 12:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'd4f8a2c6e1b9'
down_revision: Union[str, None] = 'c9d3e6b1f8a2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'risk_assessments',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('vendor_id', sa.UUID(), nullable=False),
        sa.Column(
            'overall_level',
            sa.Enum('low', 'medium', 'high', name='risklevel', native_enum=False, length=10),
            nullable=False,
        ),
        sa.Column('overall_score', sa.Float(), nullable=False),
        sa.Column('factors', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['vendor_id'], ['vendors.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_risk_assessments_vendor_id'), 'risk_assessments', ['vendor_id'], unique=False)

    op.create_table(
        'contracts',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('vendor_id', sa.UUID(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column(
            'status',
            sa.Enum(
                'draft', 'active', 'expiring', 'expired', 'terminated',
                name='contractstatus', native_enum=False, length=20,
            ),
            nullable=False,
        ),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('value', sa.Float(), nullable=True),
        sa.Column('auto_renew', sa.Boolean(), nullable=False),
        sa.Column('key_terms', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['vendor_id'], ['vendors.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_contracts_vendor_id'), 'contracts', ['vendor_id'], unique=False)
    op.create_index(op.f('ix_contracts_end_date'), 'contracts', ['end_date'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_contracts_end_date'), table_name='contracts')
    op.drop_index(op.f('ix_contracts_vendor_id'), table_name='contracts')
    op.drop_table('contracts')
    op.drop_index(op.f('ix_risk_assessments_vendor_id'), table_name='risk_assessments')
    op.drop_table('risk_assessments')
