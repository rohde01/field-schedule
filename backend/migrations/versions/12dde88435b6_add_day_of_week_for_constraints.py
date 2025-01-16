"""add day_of_week for constraints

Revision ID: 12dde88435b6
Revises: df23f7692427
Create Date: 2025-01-16 21:18:25.693965

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '12dde88435b6'
down_revision: Union[str, None] = 'df23f7692427'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('constraints', 
        sa.Column('day_of_week', sa.SMALLINT(), nullable=True)
    )
    op.create_check_constraint(
        'constraints_day_of_week_check',
        'constraints',
        'day_of_week IS NULL OR (day_of_week >= 0 AND day_of_week <= 6)'
    )


def downgrade() -> None:
    op.drop_constraint('constraints_day_of_week_check', 'constraints', type_='check')
    op.drop_column('constraints', 'day_of_week')
