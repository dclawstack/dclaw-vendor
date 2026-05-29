"""performance scores (Phase 5)

Revision ID: c9d3e6b1f8a2
Revises: b7e2f4a8c1d9
Create Date: 2026-05-30 11:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'c9d3e6b1f8a2'
down_revision: Union[str, None] = 'b7e2f4a8c1d9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'performance_scores',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('vendor_id', sa.UUID(), nullable=False),
        sa.Column('period', sa.String(length=20), nullable=False),
        sa.Column('quality_score', sa.Float(), nullable=False),
        sa.Column('delivery_score', sa.Float(), nullable=False),
        sa.Column('cost_score', sa.Float(), nullable=False),
        sa.Column('compliance_score', sa.Float(), nullable=False),
        sa.Column('overall_score', sa.Float(), nullable=False),
        sa.Column('kpis', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['vendor_id'], ['vendors.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_performance_scores_vendor_id'), 'performance_scores', ['vendor_id'], unique=False)
    op.create_index(op.f('ix_performance_scores_period'), 'performance_scores', ['period'], unique=False)
    op.create_index(op.f('ix_performance_scores_overall_score'), 'performance_scores', ['overall_score'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_performance_scores_overall_score'), table_name='performance_scores')
    op.drop_index(op.f('ix_performance_scores_period'), table_name='performance_scores')
    op.drop_index(op.f('ix_performance_scores_vendor_id'), table_name='performance_scores')
    op.drop_table('performance_scores')
