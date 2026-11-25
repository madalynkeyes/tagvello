"""Shapes of the JSON the API sends and receives.

FastAPI checks incoming JSON against these and uses them to build /docs.
Prices are Decimal so money is never a float; they're sent as strings like "8.49".
"""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


# --- products -----------------------------------------------------------------

class SearchResult(BaseModel):
    kroger_product_id: str
    upc: str | None
    name: str
    brand: str | None
    size: str | None
    image_url: str | None
    regular_price: Decimal | None
    promo_price: Decimal | None
    price: Decimal | None              # what you'd pay: promo if on sale, else regular


class StorePrice(BaseModel):
    store_id: int
    city: str | None
    price: Decimal
    regular_price: Decimal
    promo_price: Decimal | None
    observed_at: datetime


class PricePoint(BaseModel):
    """One dot on the price-history chart."""
    store_id: int
    city: str | None
    price: Decimal
    observed_at: datetime


class DealStats(BaseModel):
    """Query 5 for one product at one store."""
    store_id: int
    city: str | None
    price: Decimal
    avg_30d: Decimal
    low_30d: Decimal
    high_30d: Decimal
    pct_vs_avg: Decimal
    is_lowest_30d: bool


# --- watchlist ------------------------------------------------------------------

class WatchlistAdd(BaseModel):
    kroger_product_id: str = Field(description="kroger_product_id from a search result")


class WatchlistItem(BaseModel):
    product_id: int
    name: str
    brand: str | None
    size: str | None
    image_url: str | None
    best_price: Decimal | None         # cheapest latest price across stores
    best_store: str | None             # city of that store
    last_checked_at: datetime | None


# --- alerts ---------------------------------------------------------------------

class AlertCreate(BaseModel):
    target_price: Decimal = Field(gt=0, max_digits=10, decimal_places=2)


class AlertRule(BaseModel):
    id: int
    product_id: int
    target_price: Decimal
    enabled: bool
    created_at: datetime
