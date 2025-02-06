"""update constraint type

Revision ID: 3d21d8bb13b8
Revises: fd93ea4f4dcf
Create Date: 2025-02-06 19:51:33.776786

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3d21d8bb13b8'
down_revision: Union[str, None] = 'fd93ea4f4dcf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # Drop the old columns
    op.drop_column('constraints', 'required_size')
    op.drop_column('constraints', 'subfield_type')
    
    # Add the new required_field column with foreign key
    op.add_column('constraints', sa.Column('required_field', sa.Integer(), nullable=True))
    op.create_foreign_key(
        'fk_constraints_required_field_fields',
        'constraints',
        'fields',
        ['required_field'],
        ['field_id']
    )


def downgrade() -> None:
    # Remove the foreign key and required_field column
    op.drop_constraint('fk_constraints_required_field_fields', 'constraints', type_='foreignkey')
    op.drop_column('constraints', 'required_field')
    
    # Add back the old columns
    op.add_column('constraints', sa.Column('required_size', sa.String(), nullable=True))
    op.add_column('constraints', sa.Column('subfield_type', sa.String(), nullable=True))
    