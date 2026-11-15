"""add_role_column_to_student

Revision ID: f6a7b8c9d0e1
Revises: e5f6a7b8c9d0
Create Date: 2026-11-12 23:55:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'f6a7b8c9d0e1'
down_revision: Union[str, None] = 'e5f6a7b8c9d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    student_cols = [c['name'] for c in inspector.get_columns('student')]

    # 1. Add role column to student table if not already present
    if 'role' not in student_cols:
        op.add_column(
            'student',
            sa.Column(
                'role',
                sa.Enum('STUDENT', 'ADMIN', name='student_role_enum'),
                nullable=False,
                server_default='STUDENT'
            )
        )

    # 2. Bootstrap initial administrator account non-destructively
    op.execute(
        sa.text(
            """
            UPDATE student
            SET role = 'ADMIN'
            WHERE roll_no = '2024BTECH001'
            """
        )
    )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    student_cols = [c['name'] for c in inspector.get_columns('student')]

    if 'role' in student_cols:
        op.drop_column('student', 'role')
