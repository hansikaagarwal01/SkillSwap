"""add_department_table_and_student_fk

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-11-11 22:12:30.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'e5f6a7b8c9d0'
down_revision: Union[str, None] = 'd4e5f6a7b8c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = inspector.get_table_names()

    # 1. Create department lookup table if not exists
    if 'department' not in existing_tables:
        op.create_table(
            'department',
            sa.Column('d_id', sa.Integer(), autoincrement=False, nullable=False),
            sa.Column('name', sa.String(length=100), nullable=False),
            sa.Column('program', sa.Enum('BTECH', 'BBA', 'BDES', name='dept_program_enum'), nullable=False),
            sa.PrimaryKeyConstraint('d_id'),
        )

    # 2. Seed canonical departments idempotently
    op.execute(
        sa.text(
            """
            INSERT IGNORE INTO department (d_id, name, program) VALUES
            (1, 'Computer Science and Engineering', 'BTECH'),
            (2, 'Artificial Intelligence and Data Science', 'BTECH'),
            (3, 'Electronics and Communication Engineering', 'BTECH'),
            (4, 'Institute of Management', 'BBA'),
            (5, 'Institute of Design', 'BDES')
            """
        )
    )

    # 3. Add d_id column + FK on student if missing
    student_cols = [c['name'] for c in inspector.get_columns('student')]
    if 'd_id' not in student_cols:
        op.add_column('student', sa.Column('d_id', sa.Integer(), nullable=True))
        op.create_foreign_key(
            'fk_student_department',
            'student',
            'department',
            ['d_id'],
            ['d_id'],
            onupdate='CASCADE',
            ondelete='SET NULL',
        )

    # 4. Backfill existing students non-destructively based on program
    op.execute(
        sa.text(
            """
            UPDATE student
            SET d_id = CASE program
                WHEN 'BTECH' THEN 1
                WHEN 'BBA' THEN 4
                WHEN 'BDES' THEN 5
            END
            WHERE d_id IS NULL
            """
        )
    )


def downgrade() -> None:
    op.drop_constraint('fk_student_department', 'student', type_='foreignkey')
    op.drop_column('student', 'd_id')
    op.drop_table('department')
