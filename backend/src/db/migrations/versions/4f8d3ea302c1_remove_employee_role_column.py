"""remove employee role column

Revision ID: 4f8d3ea302c1
Revises: c7dd19dc2cb9
Create Date: 2026-03-06 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "4f8d3ea302c1"
down_revision: Union[str, Sequence[str], None] = "c7dd19dc2cb9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_column("employee", "role")
    op.execute("DROP TYPE IF EXISTS employeerole")


def downgrade() -> None:
    """Downgrade schema."""
    employeerole = postgresql.ENUM("ADMIN", "EMPLOYEE", name="employeerole")
    employeerole.create(op.get_bind(), checkfirst=True)

    op.add_column(
        "employee",
        sa.Column(
            "role",
            employeerole,
            nullable=False,
            server_default="EMPLOYEE",
        ),
    )
    op.alter_column("employee", "role", server_default=None)
