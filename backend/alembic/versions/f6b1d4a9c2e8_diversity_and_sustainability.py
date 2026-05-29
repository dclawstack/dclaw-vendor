"""vendor diversity columns + sustainability scores (Phase 7, V7.1/V7.2)

Revision ID: f6b1d4a9c2e8
Revises: e5a9c3d7b2f1
Create Date: 2026-05-30 14:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'f6b1d4a9c2e8'
down_revision: Union[str, None] = 'e5a9c3d7b2f1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('vendors', sa.Column('diverse_owned', sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column('vendors', sa.Column('diversity_categories', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('vendors', sa.Column('diversity_certified', sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column('vendors', sa.Column('certification_body', sa.String(length=120), nullable=True))
    # drop the server defaults now that existing rows are backfilled
    op.alter_column('vendors', 'diverse_owned', server_default=None)
    op.alter_column('vendors', 'diversity_certified', server_default=None)

    op.create_table(
        'sustainability_scores',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('vendor_id', sa.UUID(), nullable=False),
        sa.Column('period', sa.String(length=20), nullable=False),
        sa.Column('carbon_footprint', sa.Float(), nullable=False),
        sa.Column('environmental_score', sa.Float(), nullable=False),
        sa.Column('social_score', sa.Float(), nullable=False),
        sa.Column('governance_score', sa.Float(), nullable=False),
        sa.Column('overall_score', sa.Float(), nullable=False),
        sa.Column('targets', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['vendor_id'], ['vendors.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_sustainability_scores_vendor_id'), 'sustainability_scores', ['vendor_id'], unique=False)
    op.create_index(op.f('ix_sustainability_scores_overall_score'), 'sustainability_scores', ['overall_score'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_sustainability_scores_overall_score'), table_name='sustainability_scores')
    op.drop_index(op.f('ix_sustainability_scores_vendor_id'), table_name='sustainability_scores')
    op.drop_table('sustainability_scores')
    op.drop_column('vendors', 'certification_body')
    op.drop_column('vendors', 'diversity_certified')
    op.drop_column('vendors', 'diversity_categories')
    op.drop_column('vendors', 'diverse_owned')
