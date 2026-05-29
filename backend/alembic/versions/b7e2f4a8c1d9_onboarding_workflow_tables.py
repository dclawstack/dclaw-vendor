"""onboarding workflow: cases, documents, approval steps (Phase 4)

Revision ID: b7e2f4a8c1d9
Revises: a3c1d9f2b7e4
Create Date: 2026-05-30 10:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'b7e2f4a8c1d9'
down_revision: Union[str, None] = 'a3c1d9f2b7e4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'onboarding_cases',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('vendor_id', sa.UUID(), nullable=False),
        sa.Column(
            'status',
            sa.Enum(
                'draft', 'collecting', 'pending_approval', 'approved', 'rejected', 'activated',
                name='onboardingstatus', native_enum=False, length=20,
            ),
            nullable=False,
        ),
        sa.Column('checklist', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['vendor_id'], ['vendors.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_onboarding_cases_vendor_id'), 'onboarding_cases', ['vendor_id'], unique=False)

    op.create_table(
        'onboarding_documents',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('case_id', sa.UUID(), nullable=False),
        sa.Column('doc_type', sa.String(length=80), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('storage_key', sa.String(length=512), nullable=False),
        sa.Column('content_type', sa.String(length=120), nullable=True),
        sa.Column('size', sa.Integer(), nullable=True),
        sa.Column(
            'status',
            sa.Enum(
                'uploaded', 'validated', 'rejected',
                name='documentstatus', native_enum=False, length=20,
            ),
            nullable=False,
        ),
        sa.Column('validation', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('uploaded_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['case_id'], ['onboarding_cases.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_onboarding_documents_case_id'), 'onboarding_documents', ['case_id'], unique=False)

    op.create_table(
        'approval_steps',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('case_id', sa.UUID(), nullable=False),
        sa.Column('step_order', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=120), nullable=False),
        sa.Column('approver_role', sa.String(length=80), nullable=True),
        sa.Column(
            'status',
            sa.Enum(
                'pending', 'approved', 'rejected',
                name='approvalstatus', native_enum=False, length=20,
            ),
            nullable=False,
        ),
        sa.Column('decided_by', sa.String(length=120), nullable=True),
        sa.Column('decided_at', sa.DateTime(), nullable=True),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['case_id'], ['onboarding_cases.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_approval_steps_case_id'), 'approval_steps', ['case_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_approval_steps_case_id'), table_name='approval_steps')
    op.drop_table('approval_steps')
    op.drop_index(op.f('ix_onboarding_documents_case_id'), table_name='onboarding_documents')
    op.drop_table('onboarding_documents')
    op.drop_index(op.f('ix_onboarding_cases_vendor_id'), table_name='onboarding_cases')
    op.drop_table('onboarding_cases')
