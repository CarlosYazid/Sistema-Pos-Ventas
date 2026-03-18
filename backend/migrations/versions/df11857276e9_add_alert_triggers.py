"""add alert triggers

Revision ID: df11857276e9
Revises: de13bc3d81ac
Create Date: 2026-03-14 18:06:46.289140

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "df11857276e9"
down_revision: Union[str, Sequence[str], None] = "de13bc3d81ac"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():

    op.alter_column(
        "expirationalert", "created_at", existing_type=sa.DateTime(), server_default=sa.func.now()
    )

    op.alter_column(
        "expirationalert", "updated_at", existing_type=sa.DateTime(), server_default=sa.func.now()
    )

    op.alter_column(
        "stockalert", "created_at", existing_type=sa.DateTime(), server_default=sa.func.now()
    )

    op.alter_column(
        "stockalert", "updated_at", existing_type=sa.DateTime(), server_default=sa.func.now()
    )

    # función + trigger stock
    op.execute("""
    CREATE OR REPLACE FUNCTION insert_stock_alert()
    RETURNS trigger AS $$
    BEGIN
      IF NEW.stock <= NEW.minimum_stock THEN
        INSERT INTO stockalert (product_id, product_name, stock, minimum_stock)
        VALUES (NEW.id, NEW.name, NEW.stock, NEW.minimum_stock)
        ON CONFLICT DO NOTHING;
      END IF;
      RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """)
    op.execute("""
    CREATE TRIGGER trg_insert_stock_alert
    AFTER UPDATE ON product
    FOR EACH ROW
    WHEN (OLD.stock IS DISTINCT FROM NEW.stock)
    EXECUTE FUNCTION insert_stock_alert();
    """)

    # función + trigger expirations...
    op.execute("""
    CREATE OR REPLACE FUNCTION check_expiration_and_alert()
    RETURNS trigger AS $$
    BEGIN
      IF NEW.expiration_date IS NOT NULL AND
         NEW.expiration_date <= (CURRENT_DATE + INTERVAL '7 days') THEN
        INSERT INTO expirationalert (product_id, product_name, expiration_date)
        VALUES (NEW.id, NEW.name, NEW.expiration_date)
        ON CONFLICT DO NOTHING;
      END IF;
      RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """)
    op.execute("""
    CREATE TRIGGER trg_check_expiration
    AFTER INSERT OR UPDATE ON product
    FOR EACH ROW
    EXECUTE FUNCTION check_expiration_and_alert();
    """)


def downgrade():

    op.alter_column(
        "expirationalert", "created_at", existing_type=sa.DateTime(), server_default=None
    )

    op.alter_column(
        "expirationalert", "updated_at", existing_type=sa.DateTime(), server_default=None
    )

    op.alter_column("stockalert", "created_at", existing_type=sa.DateTime(), server_default=None)

    op.alter_column("stockalert", "updated_at", existing_type=sa.DateTime(), server_default=None)

    op.execute("DROP TRIGGER IF EXISTS trg_check_expiration ON products;")
    op.execute("DROP FUNCTION IF EXISTS check_expiration_and_alert();")
    op.execute("DROP TRIGGER IF EXISTS trg_insert_stock_alert ON products;")
    op.execute("DROP FUNCTION IF EXISTS insert_stock_alert();")
