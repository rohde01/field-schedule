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
    # Rename partial_ses_space_size to partial_field
    op.alter_column('constraints', 'partial_ses_space_size', new_column_name='partial_field')
    
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
    
    # Rename partial_field back to partial_ses_space_size
    op.alter_column('constraints', 'partial_field', new_column_name='partial_ses_space_size')
