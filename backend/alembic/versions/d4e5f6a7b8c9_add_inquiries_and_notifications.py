"""add_inquiries_and_notifications

Revision ID: d4e5f6a7b8c9
Revises: c3e1b2a4d5f6
Create Date: 2026-11-03 23:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'd4e5f6a7b8c9'
down_revision: Union[str, None] = 'c3e1b2a4d5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create marketplace_inquiry table
    op.create_table(
        'marketplace_inquiry',
        sa.Column('inquiry_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('listing_id', sa.Integer(), nullable=False),
        sa.Column('buyer_roll_no', sa.String(length=12), nullable=False),
        sa.Column('seller_roll_no', sa.String(length=12), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('inquiry_status', sa.Enum('PENDING', 'RESPONDED', 'CLOSED', name='inquiry_status_enum'), server_default='PENDING', nullable=False),
        sa.Column('email_delivery_status', sa.Enum('SENT', 'FAILED', 'SKIPPED', name='email_delivery_status_enum'), server_default='SKIPPED', nullable=False),
        sa.Column('email_delivery_error', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['listing_id'], ['listing.listing_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['buyer_roll_no'], ['student.roll_no'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['seller_roll_no'], ['student.roll_no'], ondelete='RESTRICT'),
        sa.CheckConstraint('buyer_roll_no <> seller_roll_no', name='chk_inquiry_buyer_seller_distinct'),
        sa.PrimaryKeyConstraint('inquiry_id')
    )
    op.create_index('idx_inquiry_listing', 'marketplace_inquiry', ['listing_id'])
    op.create_index('idx_inquiry_seller_status', 'marketplace_inquiry', ['seller_roll_no', 'inquiry_status'])
    op.create_index('idx_inquiry_buyer', 'marketplace_inquiry', ['buyer_roll_no'])

    # 2. Create notification table
    op.create_table(
        'notification',
        sa.Column('notification_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('recipient_roll_no', sa.String(length=12), nullable=False),
        sa.Column('inquiry_id', sa.Integer(), nullable=True),
        sa.Column('title', sa.String(length=150), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('is_read', sa.Boolean(), server_default=sa.text('0'), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['recipient_roll_no'], ['student.roll_no'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['inquiry_id'], ['marketplace_inquiry.inquiry_id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('notification_id')
    )
    op.create_index('idx_notification_recipient_read', 'notification', ['recipient_roll_no', 'is_read'])


def downgrade() -> None:
    op.drop_table('notification')
    op.drop_table('marketplace_inquiry')
