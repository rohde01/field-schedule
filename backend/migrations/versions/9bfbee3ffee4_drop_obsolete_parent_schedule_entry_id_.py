"""drop obsolete parent schedule entry id entry

Revision ID: 9bfbee3ffee4
Revises: 3d21d8bb13b8
Create Date: 2025-02-06 20:49:13.071566

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9bfbee3ffee4'
down_revision: Union[str, None] = '3d21d8bb13b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column('schedule_entries', 'parent_schedule_entry_id')


def downgrade() -> None:
    op.add_column('schedule_entries', sa.Column('parent_schedule_entry_id', sa.Integer(), nullable=True))
