"""remove is_verified from employee

Revision ID: 8dca16f2058f
Revises: 4f8d3ea302c1
Create Date: 2026-03-06 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "8dca16f2058f"
down_revision: Union[str, Sequence[str], None] = "4f8d3ea302c1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_column("employee", "is_verified")


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column(
        "employee",
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.alter_column("employee", "is_verified", server_default=None)
