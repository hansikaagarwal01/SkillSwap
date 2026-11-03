"""add_survey_audit_and_desired_skills

Revision ID: c3e1b2a4d5f6
Revises: 28314a347bc0
Create Date: 2026-11-03 21:18:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = 'c3e1b2a4d5f6'
down_revision: Union[str, None] = '28314a347bc0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Modify student table to make password_hash nullable and default account_status to UNVERIFIED, email_verified to 0
    op.alter_column('student', 'password_hash',
               existing_type=sa.String(length=255),
               nullable=True)
    op.alter_column('student', 'account_status',
               existing_type=sa.Enum('UNVERIFIED', 'PENDING_APPROVAL', 'ACTIVE', 'SUSPENDED', name='account_status_enum'),
               server_default='UNVERIFIED',
               existing_nullable=False)
    op.alter_column('student', 'email_verified',
               existing_type=sa.Boolean(),
               server_default=sa.text('0'),
               existing_nullable=False)

    # 2. Add uq_skill_name unique constraint
    try:
        op.create_unique_constraint('uq_skill_name', 'skill', ['name'])
    except Exception:
        pass

    # 3. Create student_desired_skill table
    op.create_table('student_desired_skill',
        sa.Column('roll_no', sa.String(length=12), nullable=False),
        sa.Column('skill_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['roll_no'], ['student.roll_no'], onupdate='CASCADE', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['skill_id'], ['skill.skill_id'], onupdate='CASCADE', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('roll_no', 'skill_id')
    )
    op.create_index('idx_desired_skill_skill', 'student_desired_skill', ['skill_id'], unique=False)

    # 4. Modify listing table: add original_price_text and update status enum if needed
    op.add_column('listing', sa.Column('original_price_text', sa.String(length=150), nullable=True))
    op.alter_column('listing', 'status',
        existing_type=sa.Enum('AVAILABLE', 'SOLD', 'REMOVED', 'PENDING_REVIEW', name='listing_status_enum'),
        type_=sa.Enum('AVAILABLE', 'SOLD', 'REMOVED', 'PENDING_REVIEW', name='listing_status_enum'),
        existing_nullable=False,
        server_default='AVAILABLE'
    )

    # 5. Create survey_import_audit table
    op.create_table('survey_import_audit',
        sa.Column('submission_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('survey_timestamp', sa.DateTime(), nullable=False),
        sa.Column('student_name', sa.String(length=100), nullable=False),
        sa.Column('raw_roll_no', sa.String(length=50), nullable=False),
        sa.Column('normalized_roll_no', sa.String(length=12), nullable=True),
        sa.Column('raw_email', sa.String(length=100), nullable=False),
        sa.Column('raw_current_skills', sa.Text(), nullable=True),
        sa.Column('raw_desired_skills', sa.Text(), nullable=True),
        sa.Column('raw_sell_flag', sa.String(length=10), nullable=True),
        sa.Column('raw_item', sa.String(length=255), nullable=True),
        sa.Column('raw_price', sa.String(length=100), nullable=True),
        sa.Column('raw_description', sa.Text(), nullable=True),
        sa.Column('import_status', sa.Enum('IMPORTED', 'MERGED_DUPLICATE', 'REQUIRES_REVIEW', 'REJECTED', name='import_status_enum'), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('submission_id')
    )
    op.create_index('idx_audit_roll', 'survey_import_audit', ['normalized_roll_no'], unique=False)
    op.create_index('idx_audit_status', 'survey_import_audit', ['import_status'], unique=False)


def downgrade() -> None:
    op.drop_table('survey_import_audit')
    op.drop_column('listing', 'original_price_text')
    op.drop_table('student_desired_skill')
    op.drop_constraint('uq_skill_name', 'skill', type_='unique')

