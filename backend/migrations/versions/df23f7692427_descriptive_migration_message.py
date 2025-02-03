"""Add training_length column to teams

Revision ID: df23f7692427
Revises: db978721ab79
Create Date: 2025-01-14 19:00:33.709066

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'df23f7692427'
down_revision: Union[str, None] = 'db978721ab79'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('teams',
        sa.Column('training_length', sa.Integer(), nullable=True)
    )


def downgrade() -> None:
    op.drop_column('teams', 'training_length')
