"""fix partial field type

Revision ID: 827e8389ddc9
Revises: 9bfbee3ffee4
Create Date: 2025-02-07 22:47:47.221315

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '827e8389ddc9'
down_revision: Union[str, None] = '9bfbee3ffee4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Set non-numeric values to NULL
    op.execute("UPDATE constraints SET partial_field = NULL WHERE partial_field NOT SIMILAR TO '[0-9]+'")

    # Change the column type to Integer
    op.alter_column('constraints', 'partial_field',
                    existing_type=sa.VARCHAR(),
                    type_=sa.Integer(),
                    postgresql_using='partial_field::integer',
                    existing_nullable=True)


def downgrade() -> None:
    # Change the column type back to VARCHAR
    op.alter_column('constraints', 'partial_field',
                    existing_type=sa.Integer(),
                    type_=sa.VARCHAR(),
                    postgresql_using='partial_field::varchar',
                    existing_nullable=True)
