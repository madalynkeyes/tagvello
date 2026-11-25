"""Price-drop alert rules for products on the user's watchlist."""

import psycopg
from fastapi import APIRouter, Depends, HTTPException, Response

from app.auth import get_current_user
from app.db import get_conn
from app.schemas import AlertCreate, AlertRule

router = APIRouter(tags=["alerts"])


# TODO (Madalyn)
@router.get("/alerts", response_model=list[AlertRule])
def list_alerts(
    user: dict = Depends(get_current_user),
    conn: psycopg.Connection = Depends(get_conn),
):
    """All of the user's alert rules."""
    # alert_rules JOIN watchlist_items (for product_id, and to filter by user_id).
    raise HTTPException(status_code=501, detail="Not implemented yet")


# TODO (Madalyn)
@router.post("/watchlist/{product_id}/alerts", response_model=AlertRule, status_code=201)
def create_alert(
    product_id: int,
    body: AlertCreate,
    user: dict = Depends(get_current_user),
    conn: psycopg.Connection = Depends(get_conn),
):
    """'Email me when this drops below $X.'"""
    # Find the user's active watchlist item for this product (404 if none),
    # then INSERT ... RETURNING the new rule.
    raise HTTPException(status_code=501, detail="Not implemented yet")


# TODO (Madalyn)
@router.delete("/alerts/{alert_id}", status_code=204)
def delete_alert(
    alert_id: int,
    user: dict = Depends(get_current_user),
    conn: psycopg.Connection = Depends(get_conn),
):
    """Delete one of the user's alert rules."""
    # Important: only delete it if it belongs to this user. Otherwise anyone could
    # delete anyone's alerts by guessing ids. (DELETE ... USING watchlist_items ...)
    # 404 if nothing was deleted (cur.rowcount == 0).
    raise HTTPException(status_code=501, detail="Not implemented yet")
    return Response(status_code=204)
