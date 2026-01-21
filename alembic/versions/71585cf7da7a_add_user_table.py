"""Add user table

Revision ID: 71585cf7da7a
Revises: eb5609824659
Create Date: 2025-11-03 21:10:01.870307

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '71585cf7da7a'
down_revision: Union[str, Sequence[str], None] = 'eb5609824659'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "users", 
        sa.Column("id", sa.Integer(), nullable=False, primary_key=True), 
        sa.Column("email", sa.String(), nullable=False), 
        sa.Column("password", sa.String(), nullable=False), 
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
        )
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("users")
    pass
