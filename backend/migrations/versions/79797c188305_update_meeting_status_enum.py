"""update meeting status enum

Revision ID: 79797c188305
Revises: 7adda8dbc00f
Create Date: 2025-08-07 16:40:09.872563

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "79797c188305"
down_revision: Union[str, Sequence[str], None] = "7adda8dbc00f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # The meetings table already exists, so just update the enum
    op.execute("ALTER TYPE meeting_status RENAME VALUE 'JOINED' TO 'IN_PROGRESS'")


def downgrade() -> None:
    """Downgrade schema."""
    # Revert the enum change
    op.execute("ALTER TYPE meeting_status RENAME VALUE 'IN_PROGRESS' TO 'JOINED'")
