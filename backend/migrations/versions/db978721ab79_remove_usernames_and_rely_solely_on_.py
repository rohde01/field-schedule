"""Remove usernames and rely solely on email

Revision ID: db978721ab79
Revises: 54d93393f42c
Create Date: 2025-01-05 15:52:03.612369

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'db978721ab79'
down_revision: Union[str, None] = '54d93393f42c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop the username column as we'll use email as the main identifier
    op.drop_column('users', 'username')


def downgrade() -> None:
    # Recreate the username column if we need to rollback
    # Note: This will fail if there are existing records since we can't
    # automatically generate usernames for existing users
    op.add_column('users',
        sa.Column('username', sa.VARCHAR(length=255), nullable=False)
    )
    op.create_unique_constraint('users_username_key', 'users', ['username'])
