"""add new table for schedule entry exceptions

Revision ID: d51e1bb3aa2d
Revises: 07e1b72361cb
Create Date: 2025-03-24 19:13:04.721366

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd51e1bb3aa2d'
down_revision: Union[str, None] = '07e1b72361cb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'schedule_entry_overrides',
        sa.Column('override_id', sa.Integer(), nullable=False),
        sa.Column('active_schedule_id', sa.Integer(), nullable=False),
        sa.Column('schedule_entry_id', sa.Integer(), nullable=True),
        sa.Column('override_date', sa.Date(), nullable=False),
        sa.Column('new_start_time', sa.Time(), nullable=True),
        sa.Column('new_end_time', sa.Time(), nullable=True),
        sa.Column('new_team_id', sa.Integer(), nullable=True),
        sa.Column('new_field_id', sa.Integer(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.PrimaryKeyConstraint('override_id'),
        sa.ForeignKeyConstraint(
            ['active_schedule_id'],
            ['active_schedules.active_schedule_id'],
            name='fk_active_schedule',
            ondelete='CASCADE'
        ),
        sa.ForeignKeyConstraint(
            ['schedule_entry_id'],
            ['schedule_entries.schedule_entry_id'],
            name='fk_schedule_entry',
            ondelete='CASCADE'
        ),
        sa.UniqueConstraint('active_schedule_id', 'override_date', 'schedule_entry_id', name='unique_override')
    )


def downgrade() -> None:
    op.drop_table('schedule_entry_overrides')
