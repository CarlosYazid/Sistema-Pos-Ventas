"""add invoice fields to order

Revision ID: f8c2b0b4b3e1
Revises: 8dca16f2058f
Create Date: 2026-03-13 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f8c2b0b4b3e1"
down_revision: Union[str, Sequence[str], None] = "8dca16f2058f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("order", sa.Column("verification_token", sa.String(length=160), nullable=True))
    op.add_column("order", sa.Column("pdf_key", sa.String(length=512), nullable=True))
    op.create_index(
        op.f("ix_order_verification_token"),
        "order",
        ["verification_token"],
        unique=True,
    )
    op.create_index(op.f("ix_order_pdf_key"), "order", ["pdf_key"], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_order_pdf_key"), table_name="order")
    op.drop_index(op.f("ix_order_verification_token"), table_name="order")
    op.drop_column("order", "pdf_key")
    op.drop_column("order", "verification_token")
