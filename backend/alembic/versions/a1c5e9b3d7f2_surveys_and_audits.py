"""surveys + audits (Phase 7, V7.3/V7.4)

Revision ID: a1c5e9b3d7f2
Revises: f6b1d4a9c2e8
Create Date: 2026-05-30 15:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1c5e9b3d7f2'
down_revision: Union[str, None] = 'f6b1d4a9c2e8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'surveys',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('vendor_id', sa.UUID(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['vendor_id'], ['vendors.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_surveys_vendor_id'), 'surveys', ['vendor_id'], unique=False)

    op.create_table(
        'survey_responses',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('survey_id', sa.UUID(), nullable=False),
        sa.Column('respondent', sa.String(length=120), nullable=True),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('sentiment', sa.String(length=20), nullable=True),
        sa.Column('sentiment_score', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['survey_id'], ['surveys.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_survey_responses_survey_id'), 'survey_responses', ['survey_id'], unique=False)

    op.create_table(
        'audits',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('vendor_id', sa.UUID(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column(
            'status',
            sa.Enum('scheduled', 'in_progress', 'completed', 'closed',
                    name='auditstatus', native_enum=False, length=20),
            nullable=False,
        ),
        sa.Column('scheduled_date', sa.Date(), nullable=True),
        sa.Column('auditor', sa.String(length=120), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['vendor_id'], ['vendors.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_audits_vendor_id'), 'audits', ['vendor_id'], unique=False)

    op.create_table(
        'audit_findings',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('audit_id', sa.UUID(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column(
            'severity',
            sa.Enum('low', 'medium', 'high', 'critical',
                    name='findingseverity', native_enum=False, length=20),
            nullable=False,
        ),
        sa.Column(
            'status',
            sa.Enum('open', 'remediating', 'closed',
                    name='findingstatus', native_enum=False, length=20),
            nullable=False,
        ),
        sa.Column('remediation', sa.Text(), nullable=True),
        sa.Column('closed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['audit_id'], ['audits.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_audit_findings_audit_id'), 'audit_findings', ['audit_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_audit_findings_audit_id'), table_name='audit_findings')
    op.drop_table('audit_findings')
    op.drop_index(op.f('ix_audits_vendor_id'), table_name='audits')
    op.drop_table('audits')
    op.drop_index(op.f('ix_survey_responses_survey_id'), table_name='survey_responses')
    op.drop_table('survey_responses')
    op.drop_index(op.f('ix_surveys_vendor_id'), table_name='surveys')
    op.drop_table('surveys')
