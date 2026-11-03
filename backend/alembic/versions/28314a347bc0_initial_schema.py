"""initial_schema

Revision ID: 28314a347bc0
Revises: 
Create Date: 2026-10-22 19:27:57.519042

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '28314a347bc0'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Student
    op.create_table('student',
    sa.Column('roll_no', sa.String(length=12), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('email', sa.String(length=100), nullable=False),
    sa.Column('phone', sa.String(length=20), nullable=True),
    sa.Column('program', sa.Enum('BTECH', 'BBA', 'BDES', name='student_program_enum'), nullable=False),
    sa.Column('admission_year', sa.SmallInteger(), nullable=False),
    sa.Column('reputation_points', sa.Integer(), nullable=False, server_default='0'),
    sa.Column('password_hash', sa.String(length=255), nullable=False),
    sa.Column('account_status', sa.Enum('UNVERIFIED', 'PENDING_APPROVAL', 'ACTIVE', 'SUSPENDED', name='account_status_enum'), nullable=False, server_default='ACTIVE'),
    sa.Column('email_verified', sa.Boolean(), nullable=False, server_default=sa.text('1')),
    sa.Column('last_login_at', sa.DateTime(), nullable=True),
    sa.Column('token_version', sa.Integer(), nullable=False, server_default='1'),
    sa.Column('verification_token_hash', sa.String(length=64), nullable=True),
    sa.Column('verification_token_expires_at', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint("roll_no REGEXP '^(20[0-9]{2})(BTECH|BBA|BDES)[0-9]{3}$'", name='chk_student_roll_no_format'),
    sa.CheckConstraint('program = SUBSTRING(roll_no, 5, LENGTH(program))', name='chk_student_program_matches_roll'),
    sa.CheckConstraint('reputation_points >= 0', name='chk_student_reputation_positive'),
    sa.PrimaryKeyConstraint('roll_no'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('verification_token_hash', name='uq_student_verification_token')
    )
    op.create_index('idx_student_program_year', 'student', ['program', 'admission_year'], unique=False)
    op.create_index('idx_student_reputation', 'student', ['reputation_points'], unique=False)

    # 2. Skill
    op.create_table('skill',
    sa.Column('skill_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('category', sa.String(length=50), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('skill_id')
    )
    op.create_index('idx_skill_name', 'skill', ['name'], unique=False)
    op.create_index('idx_skill_category', 'skill', ['category'], unique=False)

    # 3. Student Skill
    op.create_table('student_skill',
    sa.Column('roll_no', sa.String(length=12), nullable=False),
    sa.Column('skill_id', sa.Integer(), nullable=False),
    sa.Column('proficiency_level', sa.Enum('BEGINNER', 'INTERMEDIATE', 'ADVANCED', 'EXPERT', name='proficiency_level_enum'), nullable=False),
    sa.Column('can_teach', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['roll_no'], ['student.roll_no'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['skill_id'], ['skill.skill_id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('roll_no', 'skill_id')
    )
    op.create_index('idx_student_skill_skill', 'student_skill', ['skill_id'], unique=False)
    op.create_index('idx_student_skill_teach', 'student_skill', ['can_teach', 'skill_id'], unique=False)

    # 4. Learning Session
    op.create_table('learning_session',
    sa.Column('session_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('mentor_roll_no', sa.String(length=12), nullable=False),
    sa.Column('learner_roll_no', sa.String(length=12), nullable=False),
    sa.Column('skill_id', sa.Integer(), nullable=False),
    sa.Column('topic', sa.String(length=255), nullable=False),
    sa.Column('mode', sa.Enum('ONLINE', 'OFFLINE', name='session_mode_enum'), nullable=False),
    sa.Column('scheduled_at', sa.DateTime(), nullable=False),
    sa.Column('meeting_link', sa.String(length=255), nullable=True),
    sa.Column('status', sa.Enum('REQUESTED', 'ACCEPTED', 'REJECTED', 'CANCELLED', 'COMPLETED', name='session_status_enum'), nullable=False),
    sa.Column('credit_cost', sa.Integer(), nullable=False, server_default='0'),
    sa.Column('points_awarded', sa.Integer(), nullable=False, server_default='0'),
    sa.Column('reputation_awarded', sa.Boolean(), nullable=False, server_default=sa.text('0')),
    sa.Column('reputation_awarded_at', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint('credit_cost = 0', name='chk_session_free_credit_cost'),
    sa.CheckConstraint('mentor_roll_no <> learner_roll_no', name='chk_session_distinct_participants'),
    sa.ForeignKeyConstraint(['learner_roll_no'], ['student.roll_no'], onupdate='RESTRICT', ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['mentor_roll_no'], ['student.roll_no'], onupdate='RESTRICT', ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['skill_id'], ['skill.skill_id'], onupdate='RESTRICT', ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('session_id')
    )
    op.create_index('idx_session_learner', 'learning_session', ['learner_roll_no'], unique=False)
    op.create_index('idx_session_mentor', 'learning_session', ['mentor_roll_no'], unique=False)
    op.create_index('idx_session_skill', 'learning_session', ['skill_id'], unique=False)
    op.create_index('idx_session_status_scheduled', 'learning_session', ['status', 'scheduled_at'], unique=False)

    # 5. Review
    op.create_table('review',
    sa.Column('session_id', sa.Integer(), nullable=False),
    sa.Column('roll_no', sa.String(length=12), nullable=False),
    sa.Column('reviewee_roll_no', sa.String(length=12), nullable=False),
    sa.Column('rating', sa.SmallInteger(), nullable=False),
    sa.Column('comment', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint('rating BETWEEN 1 AND 5', name='chk_review_rating_range'),
    sa.CheckConstraint('roll_no <> reviewee_roll_no', name='chk_review_distinct_parties'),
    sa.ForeignKeyConstraint(['reviewee_roll_no'], ['student.roll_no'], onupdate='RESTRICT', ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['roll_no'], ['student.roll_no'], onupdate='RESTRICT', ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['session_id'], ['learning_session.session_id'], onupdate='RESTRICT', ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('session_id', 'roll_no')
    )
    op.create_index('idx_review_reviewee', 'review', ['reviewee_roll_no'], unique=False)
    op.create_index('idx_review_roll', 'review', ['roll_no'], unique=False)

    # 6. Experience
    op.create_table('experience',
    sa.Column('roll_no', sa.String(length=12), nullable=False),
    sa.Column('exp_no', sa.Integer(), nullable=False),
    sa.Column('role_title', sa.String(length=150), nullable=False),
    sa.Column('organization', sa.String(length=150), nullable=False),
    sa.Column('exp_type', sa.Enum('INTERNSHIP', 'PROJECT', 'HACKATHON', 'ACHIEVEMENT', 'OTHER', name='exp_type_enum'), nullable=False),
    sa.Column('start_date', sa.Date(), nullable=False),
    sa.Column('end_date', sa.Date(), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint('end_date IS NULL OR end_date >= start_date', name='chk_experience_dates'),
    sa.ForeignKeyConstraint(['roll_no'], ['student.roll_no'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('roll_no', 'exp_no')
    )

    # 7. Listing
    op.create_table('listing',
    sa.Column('listing_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('seller_roll_no', sa.String(length=12), nullable=False),
    sa.Column('buyer_roll_no', sa.String(length=12), nullable=True),
    sa.Column('title', sa.String(length=200), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('status', sa.Enum('AVAILABLE', 'SOLD', 'REMOVED', name='listing_status_enum'), nullable=False),
    sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('category', sa.String(length=50), nullable=False),
    sa.Column('item_condition', sa.Enum('NEW', 'LIKE_NEW', 'GOOD', 'FAIR', name='item_condition_enum'), nullable=False),
    sa.Column('posted_date', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('sold_at', sa.DateTime(), nullable=True),
    sa.CheckConstraint('(status = \'SOLD\' AND buyer_roll_no IS NOT NULL AND sold_at IS NOT NULL) OR (status <> \'SOLD\')', name='chk_listing_sold_consistency'),
    sa.CheckConstraint('buyer_roll_no IS NULL OR seller_roll_no <> buyer_roll_no', name='chk_listing_seller_buyer_distinct'),
    sa.CheckConstraint('price >= 0', name='chk_listing_price_positive'),
    sa.ForeignKeyConstraint(['buyer_roll_no'], ['student.roll_no'], onupdate='RESTRICT', ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['seller_roll_no'], ['student.roll_no'], onupdate='RESTRICT', ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('listing_id')
    )
    op.create_index('idx_listing_buyer', 'listing', ['buyer_roll_no'], unique=False)
    op.create_index('idx_listing_seller', 'listing', ['seller_roll_no'], unique=False)
    op.create_index('idx_listing_status_category', 'listing', ['status', 'category'], unique=False)


def downgrade() -> None:
    op.drop_table('listing')
    op.drop_table('experience')
    op.drop_table('review')
    op.drop_table('learning_session')
    op.drop_table('student_skill')
    op.drop_table('skill')
    op.drop_table('student')
