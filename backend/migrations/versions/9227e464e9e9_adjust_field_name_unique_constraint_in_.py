"""adjust field name unique constraint in fields table

Revision ID: 9227e464e9e9
Revises: 57fd959e2426
Create Date: 2025-01-03 10:52:38.625135

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9227e464e9e9'
down_revision: Union[str, None] = '57fd959e2426'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop the existing unique constraint
    op.drop_constraint('fields_facility_id_name_key', 'fields', type_='unique')
    
    # Add new partial unique constraint
    op.create_index(
        'fields_facility_id_name_active_idx',
        'fields',
        ['facility_id', 'name'],
        unique=True,
        postgresql_where=sa.text('is_active = true')
    )


def downgrade() -> None:
    # Drop the partial unique constraint
    op.drop_index('fields_facility_id_name_active_idx', table_name='fields')
    
    # Recreate the original unique constraint
    op.create_unique_constraint(
        'fields_facility_id_name_key',
        'fields',
        ['facility_id', 'name']
    )
