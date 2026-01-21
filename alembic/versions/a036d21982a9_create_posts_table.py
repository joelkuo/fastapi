"""create posts table

Revision ID: a036d21982a9
Revises: 
Create Date: 2025-11-01 14:34:09.738695

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a036d21982a9'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "posts", 
        sa.Column("id", sa.Integer(), nullable=False, primary_key=True), 
        sa.Column("title", sa.String(), nullable=False), 
        # sa.Column("published", sa.Boolean(), nullable=False, server_default='TRUE'), 
        # sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()')), 
        # sa.Column("owner_id", sa.Integer(), nullable=False), sa.ForeignKey("users.id", ondelete="CASCADE"))
    )
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("posts")
    pass
