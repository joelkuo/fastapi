"""auto-vote

Revision ID: b4fded37fc9f
Revises: 47d3b5564efa
Create Date: 2025-11-03 21:28:26.134266

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'b4fded37fc9f'
down_revision: Union[str, Sequence[str], None] = '47d3b5564efa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # This migration was auto-generated incorrectly and would drop all tables
    # Fixed to be a no-op to prevent data loss
    # The votes table was already created in a previous migration
    pass


def downgrade() -> None:
    """Downgrade schema."""
    # This migration was auto-generated incorrectly
    # Fixed to be a no-op to prevent data loss
    pass
