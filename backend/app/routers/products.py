"""Product search, store comparison, price history, and deal stats."""

import psycopg
from fastapi import APIRouter, Depends, HTTPException, Query

from app.db import get_conn
from app.deps import get_kroger
from app.kroger import KrogerClient
from app.schemas import DealStats, PricePoint, SearchResult, StorePrice

router = APIRouter(prefix="/products", tags=["products"])


def _require_product(conn: psycopg.Connection, product_id: int) -> None:
    """404 if we don't track this product, instead of quietly returning an empty list."""
    if conn.execute("SELECT 1 FROM products WHERE id = %s", (product_id,)).fetchone() is None:
        raise HTTPException(status_code=404, detail="Product not found")


# Search Smith's products by keyword, priced at one store.
@router.get("/search", response_model=list[SearchResult])
def search_products(
    q: str = Query(min_length=2, description="Search term, e.g. 'cheddar'"),
    store_id: int | None = Query(None, description="Tagvello store id to price at (default: first store)"),
    conn: psycopg.Connection = Depends(get_conn),
    kroger: KrogerClient = Depends(get_kroger),
):
    """Search Smith's products by keyword, priced at one store."""
    if store_id is None:
        store = conn.execute("SELECT external_location_id FROM stores ORDER BY id LIMIT 1").fetchone()
    else:
        store = conn.execute("SELECT external_location_id FROM stores WHERE id = %s", (store_id,)).fetchone()
    if store is None:
        raise HTTPException(status_code=404, detail="Store not found")

    return [
        SearchResult(
            kroger_product_id=p.product_id,
            upc=p.upc,
            name=p.description,
            brand=p.brand,
            size=p.size,
            image_url=p.image_url,
            regular_price=p.regular_price,
            promo_price=p.promo_price,
            price=p.effective_price,
        )
        for p in kroger.search_products(q, store["external_location_id"])
    ]


# Compare the latest price at each store for a product id, cheapest first.
@router.get("/{product_id}/stores", response_model=list[StorePrice])
def compare_stores(product_id: int, conn: psycopg.Connection = Depends(get_conn)):
    """Latest price at each store, cheapest first."""
    _require_product(conn, product_id)
    return conn.execute(
        """
        WITH latest AS (
            SELECT DISTINCT ON (listing_id)
                listing_id,
                COALESCE(promo_price, regular_price) AS price,
                regular_price,
                promo_price,
                observed_at
            FROM price_observations
            ORDER BY listing_id, observed_at DESC
        )
        SELECT s.id AS store_id, s.city, latest.price, latest.regular_price,
               latest.promo_price, latest.observed_at
        FROM latest
        JOIN listings l ON latest.listing_id = l.id
        JOIN stores s   ON l.store_id = s.id
        WHERE l.product_id = %s
        ORDER BY latest.price, s.city
        """,
        (product_id,),
    ).fetchall()


# Get all the recorded prices for this product at every store over the last 'days' days
@router.get("/{product_id}/history", response_model=list[PricePoint])
def price_history(
    product_id: int,
    days: int = Query(30, ge=1, le=365),
    conn: psycopg.Connection = Depends(get_conn),
):
    """Every recorded price for this product at every store over the last `days` days."""
    _require_product(conn, product_id)
    return conn.execute(
        """
        SELECT s.id AS store_id, s.city, COALESCE(po.promo_price, po.regular_price) AS price,
        po.observed_at
        FROM price_observations po
        JOIN listings l ON po.listing_id = l.id
        JOIN stores s ON l.store_id = s.id
        WHERE l.product_id = %s AND po.observed_at > NOW() - make_interval(days => %s)
        ORDER BY po.observed_at, s.id;"""
        ,(product_id, days,)
    ).fetchall()




# Determine if the current price is a good deal, compared to the last 30 days of prices. One row per store.
@router.get("/{product_id}/stats", response_model=list[DealStats])
def deal_stats(product_id: int, conn: psycopg.Connection = Depends(get_conn)):
    """Is the current price a good deal? One row per store."""
    _require_product(conn, product_id)
    return conn.execute(
        """
        WITH latest AS (     -- query 1
            SELECT DISTINCT ON (listing_id)
            listing_id,
            COALESCE(promo_price, regular_price) AS price,
            observed_at
            FROM price_observations
            ORDER BY listing_id, observed_at DESC                                 
        ),
        stats AS (
            SELECT
                listing_id,
                min(COALESCE(promo_price,regular_price))            AS low_30d,
                max(COALESCE(promo_price,regular_price))            AS high_30d,
                avg(COALESCE(promo_price,regular_price))            AS avg_raw,   
                round(avg(COALESCE(promo_price,regular_price)), 2)  AS avg_30d   
            FROM price_observations
            WHERE observed_at > (NOW() - INTERVAL '30 days')   
            GROUP BY listing_id
        )
        SELECT
            s.city,
            s.id AS store_id,
            latest.price,
            stats.avg_30d,
            stats.low_30d,
            stats.high_30d,
            round((latest.price - stats.avg_raw) / stats.avg_raw * 100, 1)   AS pct_vs_avg,
            latest.price <= stats.low_30d AND stats.low_30d < stats.high_30d  AS is_lowest_30d
        FROM latest
        JOIN stats      ON latest.listing_id = stats.listing_id
        JOIN listings l ON stats.listing_id = l.id
        JOIN stores s   ON l.store_id = s.id
        WHERE l.product_id = %s
        ORDER BY pct_vs_avg
    """, (product_id,)
    ).fetchall()
