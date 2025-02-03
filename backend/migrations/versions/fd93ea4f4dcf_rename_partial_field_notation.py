"""rename partial field notation

Revision ID: fd93ea4f4dcf
Revises: b14542ca848e
Create Date: 2025-01-18 23:03:01.750013

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fd93ea4f4dcf'
down_revision: Union[str, None] = 'b14542ca848e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('constraints', 'partial_ses_space_size', new_column_name='partial_field')


def downgrade() -> None:
    op.alter_column('constraints', 'partial_field', new_column_name='partial_ses_space_size')
