from datetime import date
from typing import Optional, TYPE_CHECKING

from sqlmodel import Field, Relationship
from sqlalchemy import Index, text

from .abc import BaseModel

if TYPE_CHECKING:
    from .product import Product


class AlertBase(BaseModel):
    
    product_name: str
    product_id: int = Field(foreign_key="product.id")
    notified: bool = Field(default=False)

class StockAlert(AlertBase, table=True):

    __table_args__ = (
        Index(
            "idx_stock_alerts_notified_false",
            "product_id",
            postgresql_where=text("notified = false"),
        ),
    )

    stock: int
    minimum_stock: int
    
    product: "Product" = Relationship(
      back_populates="stock_alert", sa_relationship_kwargs={"lazy": "selectin"}
    )

class ExpirationAlert(AlertBase, table=True):

    __table_args__ = (
        Index(
            "idx_expiration_alerts_notified_false",
            "product_id",
            postgresql_where=text("notified = false"),
        ),
    )

    expiration_date: Optional[date] = None

    product: "Product" = Relationship(
      back_populates="expiration_alert", sa_relationship_kwargs={"lazy": "selectin"}
    )

"""

create or replace function delete_notified_stock_alerts()
returns trigger as $$
begin
  if NEW.notified = true then
    delete from stock_alerts where id = NEW.id;
  end if;
  return null;  -- No se sigue con el UPDATE porque el registro se elimina
end;
$$ language plpgsql;

create trigger delete_stock_alert_after_notified
after update on stock_alerts
for each row
when (OLD.notified is distinct from NEW.notified)
execute function delete_notified_stock_alerts();

create or replace function delete_notified_expiration_alerts()
returns trigger as $$
begin
  if NEW.notified = true then
    delete from expiration_alerts where id = NEW.id;
  end if;
  return null; -- No se necesita continuar con el UPDATE si se eliminó
end;
$$ language plpgsql;

create trigger delete_alert_after_notified
after update on expiration_alerts
for each row
when (OLD.notified is distinct from NEW.notified) -- solo si cambia el valor
execute function delete_notified_expiration_alerts();

"""