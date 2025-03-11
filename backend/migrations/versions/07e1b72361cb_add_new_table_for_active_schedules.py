"""add new table for active schedules

Revision ID: 07e1b72361cb
Revises: 827e8389ddc9
Create Date: 2025-03-11 17:01:01.948078

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '07e1b72361cb'
down_revision: Union[str, None] = '827e8389ddc9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Ensure btree_gist extension is available
    op.execute("CREATE EXTENSION IF NOT EXISTS btree_gist;")

    # Create the active_schedules table
    op.create_table(
        'active_schedules',
        sa.Column('active_schedule_id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('club_id', sa.Integer, nullable=False),
        sa.Column('schedule_id', sa.Integer, nullable=False),
        sa.Column('start_date', sa.Date, nullable=False),
        sa.Column('end_date', sa.Date, nullable=False),
        sa.Column('is_active', sa.Boolean, nullable=False, server_default=sa.sql.expression.true()),
        sa.Column('created_at', sa.TIMESTAMP(timezone=False), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['club_id'], ['clubs.club_id'], ondelete='CASCADE', name='fk_active_schedules_club'),
        sa.ForeignKeyConstraint(['schedule_id'], ['schedules.schedule_id'], ondelete='CASCADE', name='fk_active_schedules_schedule'),
        sa.CheckConstraint('start_date < end_date', name='active_schedules_no_invalid_dates')
    )

    # Add the EXCLUDE constraint to prevent overlapping active schedules for the same club
    op.execute("""
        ALTER TABLE active_schedules ADD CONSTRAINT no_overlapping_active_schedules
        EXCLUDE USING GIST (club_id WITH =, daterange(start_date, end_date, '[]') WITH &&);
    """)


def downgrade() -> None:
    # Drop the table first to avoid foreign key conflicts
    op.drop_table('active_schedules')

    # Remove the extension
    op.execute("DROP EXTENSION IF EXISTS btree_gist;")
