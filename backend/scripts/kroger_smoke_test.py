"""
Kroger API smoke test for Tagvello.

Checks three things before any app code is written:
  1. Our client credentials can get an OAuth access token.
  2. The Locations API can find Smith's stores near Provo and Orem.
  3. The Products API returns per-store regular and promo prices.

Run from the backend/ folder with the venv active:
    python scripts/kroger_smoke_test.py
    python scripts/kroger_smoke_test.py "eggs"      # search a different term
"""

import base64
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

# .env lives in the repo root, two levels up from this file.
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

BASE_URL = os.getenv("KROGER_BASE_URL", "https://api.kroger.com/v1").rstrip("/")
CLIENT_ID = os.getenv("KROGER_CLIENT_ID")
CLIENT_SECRET = os.getenv("KROGER_CLIENT_SECRET")

ZIP_CODES = {"Provo": "84604", "Orem": "84057", "Saratoga Springs": "84045", "Lehi": "84043"}


def get_token() -> str:
    """OAuth 2.0 client-credentials flow: trade our ID + secret for a short-lived token."""
    if not CLIENT_ID or not CLIENT_SECRET:
        sys.exit("Missing KROGER_CLIENT_ID or KROGER_CLIENT_SECRET in .env")

    # The ID and secret are sent together as HTTP Basic auth: base64("id:secret").
    basic = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    resp = requests.post(
        f"{BASE_URL}/connect/oauth2/token",
        headers={
            "Authorization": f"Basic {basic}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data={"grant_type": "client_credentials", "scope": "product.compact"},
        timeout=15,
    )
    if resp.status_code != 200:
        sys.exit(f"Token request failed ({resp.status_code}): {resp.text}")

    body = resp.json()
    print(f"1. Got a token (expires in {body.get('expires_in')} seconds)\n")
    return body["access_token"]


def find_smiths_stores(token: str) -> list[dict]:
    """Look up Smith's stores near each zip code and print their location IDs."""
    print("2. Smith's stores found:")
    stores = []
    for city, zip_code in ZIP_CODES.items():
        resp = requests.get(
            f"{BASE_URL}/locations",
            headers={"Authorization": f"Bearer {token}"},
            params={
                "filter.zipCode.near": zip_code,
                "filter.radiusInMiles": 5,
                "filter.limit": 10,
            },
            timeout=15,
        )
        resp.raise_for_status()
        for loc in resp.json().get("data", []):
            if "SMITH" not in (loc.get("chain", "") + loc.get("name", "")).upper():
                continue
            addr = loc.get("address", {})
            store = {
                "location_id": loc["locationId"],
                "name": loc.get("name"),
                "address": f"{addr.get('addressLine1')}, {addr.get('city')} {addr.get('zipCode')}",
            }
            if store["location_id"] not in {s["location_id"] for s in stores}:
                stores.append(store)
                print(f"   [{city}] {store['location_id']}  {store['name']}  -  {store['address']}")
    print()
    if not stores:
        sys.exit("No Smith's stores found. Check the zip codes or try a larger radius.")
    return stores


def search_products(token: str, location_id: str, term: str) -> None:
    """Search products at one store. Prices only come back when a locationId is given."""
    resp = requests.get(
        f"{BASE_URL}/products",
        headers={"Authorization": f"Bearer {token}"},
        params={"filter.term": term, "filter.locationId": location_id, "filter.limit": 5},
        timeout=15,
    )
    resp.raise_for_status()
    products = resp.json().get("data", [])
    print(f"3. '{term}' at store {location_id}:")
    if not products:
        print("   No products returned.")
    for p in products:
        item = (p.get("items") or [{}])[0]
        price = item.get("price") or {}
        regular, promo = price.get("regular"), price.get("promo")
        sale = f"  SALE ${promo}" if promo and promo != regular else ""
        print(
            f"   {p.get('productId')}  UPC {p.get('upc')}  {p.get('brand')} - "
            f"{p.get('description')} ({item.get('size')})  regular ${regular}{sale}"
        )
    print()


if __name__ == "__main__":
    term = sys.argv[1] if len(sys.argv) > 1 else "cheddar cheese"
    token = get_token()
    stores = find_smiths_stores(token)
    # Search the first two stores so you can compare prices side by side.
    for store in stores[:4]:
        search_products(token, store["location_id"], term)
