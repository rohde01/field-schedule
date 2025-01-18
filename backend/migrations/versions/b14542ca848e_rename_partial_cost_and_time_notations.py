"""rename partial cost and time notations

Revision ID: b14542ca848e
Revises: 12dde88435b6
Create Date: 2025-01-18 10:39:20.856299

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b14542ca848e'
down_revision: Union[str, None] = '12dde88435b6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('constraints', 'partial_ses_time', new_column_name='partial_time')
    op.alter_column('constraints', 'partial_ses_space_cost', new_column_name='partial_cost')


def downgrade() -> None:
    op.alter_column('constraints', 'partial_time', new_column_name='partial_ses_time')
    op.alter_column('constraints', 'partial_cost', new_column_name='partial_ses_space_cost')
