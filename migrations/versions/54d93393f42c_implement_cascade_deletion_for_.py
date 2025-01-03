"""Implement cascade deletion for schedules and constraints

Revision ID: 54d93393f42c
Revises: 9227e464e9e9
Create Date: 2025-01-03 15:31:35.959469

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "54d93393f42c"
down_revision: Union[str, None] = "9227e464e9e9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    1. Create a foreign key from schedule_entries to schedules with ON DELETE CASCADE.
    2. Create a foreign key from constraints to schedule_entries with ON DELETE CASCADE.
    """
    # 1. schedule_entries -> schedules
    op.create_foreign_key(
        "fk_schedule_entries_schedules",
        "schedule_entries",
        "schedules",
        ["schedule_id"],
        ["schedule_id"],
        ondelete="CASCADE",
    )

    # 2. constraints -> schedule_entries
    op.create_foreign_key(
        "fk_constraints_schedule_entries",
        "constraints",
        "schedule_entries",
        ["schedule_entry_id"],
        ["schedule_entry_id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    """
    Drop the foreign keys added in the upgrade.
    """
    op.drop_constraint("fk_constraints_schedule_entries", "constraints", type_="foreignkey")
    op.drop_constraint("fk_schedule_entries_schedules", "schedule_entries", type_="foreignkey")
