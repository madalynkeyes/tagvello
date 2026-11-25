"""The signed-in user's watchlist."""

import psycopg
from fastapi import APIRouter, Depends, HTTPException, Response

from app.auth import get_current_user
from app.db import get_conn
from app.deps import get_kroger
from app.kroger import KrogerClient
from app.schemas import WatchlistAdd, WatchlistItem
from app.catalog import track_product

router = APIRouter(prefix="/watchlist", tags=["watchlist"])

def fetch_watchlist(
    conn: psycopg.Connection, 
    user_id,
    product_id: int | None = None
) -> list[dict]:
    """Everything the user is watching, with the cheapest latest price across stores,
        pass in a product_id to get just that one item"""
    return conn.execute(
        """
        WITH watchlist AS (
            SELECT product_id
            FROM watchlist_items
            WHERE user_id = %(user_id)s 
            AND active = true
            AND (%(product_id)s::bigint IS NULL OR product_id = %(product_id)s)
        ),
        latest AS (
            SELECT DISTINCT ON (listing_id)
                listing_id,
                COALESCE(promo_price, regular_price) AS price,
                observed_at
            FROM price_observations
            ORDER BY listing_id, observed_at DESC
        ),
        best AS (                          
            SELECT DISTINCT ON (l.product_id)
                l.product_id, latest.price, s.city
            FROM latest
            JOIN listings l ON latest.listing_id = l.id
            JOIN stores s   ON l.store_id = s.id
            ORDER BY l.product_id, latest.price, s.city
        ),
        checked AS (                      
            SELECT product_id, max(last_checked_at) AS last_checked_at
            FROM listings
            GROUP BY product_id
        )
        SELECT p.id AS product_id, p.name, p.brand, p.size, p.image_url,
               best.price AS best_price, best.city AS best_store,
               checked.last_checked_at
        FROM watchlist w
        JOIN products p   ON w.product_id = p.id
        LEFT JOIN best    ON best.product_id = p.id
        LEFT JOIN checked ON checked.product_id = p.id
        ORDER BY p.name
        """,{"user_id":user_id,"product_id":product_id}
    ).fetchall()


# Gets items in watchlist and tracks what the best price is right now
@router.get("", response_model=list[WatchlistItem])
def get_watchlist(
    user: dict = Depends(get_current_user),
    conn: psycopg.Connection = Depends(get_conn),
):
    """Everything the user is watching, with the cheapest latest price across stores."""
    return fetch_watchlist(conn,user["id"])


# Add product to watchlist
@router.post("", response_model=WatchlistItem, status_code=201)
def add_to_watchlist(
    body: WatchlistAdd,
    user: dict = Depends(get_current_user),
    conn: psycopg.Connection = Depends(get_conn),
    kroger: KrogerClient = Depends(get_kroger),
):
    """Watch a product from a search result. Starts tracking it at every store."""
    stores = conn.execute("SELECT external_location_id FROM stores ORDER BY id").fetchall()
    product = None
    for store in stores:
        product = kroger.get_product(body.kroger_product_id,store["external_location_id"])
        if product is not None:
            break
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    if not product.upc:
        raise HTTPException(status_code=422,detail="This product has no UPC, so it can't be tracked")
    product_id = track_product(conn,product)
    conn.execute(
        """
        INSERT INTO watchlist_items (user_id, product_id)
        VALUES (%s,%s)
        ON CONFLICT (user_id, product_id) DO UPDATE
        SET active = true
        """,(user["id"],product_id)
    )
    # TODO (next session): a product that is new to Tagvello has no prices yet, so
    # best_price/best_store/last_checked_at come back empty until the next daily ingest.
    # Fix: record a first price at every store here (inside a small ingestion run),
    # reusing the per-listing logic from worker/ingest.py via a shared function.
    return fetch_watchlist(conn,user["id"],product_id)[0]






# TODO (Madalyn)
@router.delete("/{product_id}", status_code=204)
def remove_from_watchlist(
    product_id: int,
    user: dict = Depends(get_current_user),
    conn: psycopg.Connection = Depends(get_conn),
):
    """Stop watching a product."""
    # Decide: delete the row, or set active = false (keeps history, and the
    # alert rules can be disabled instead of deleted)? 404 if it isn't on the list.
    raise HTTPException(status_code=501, detail="Not implemented yet")
    return Response(status_code=204)
