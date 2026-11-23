"""
Do Smith's prices differ by store? Compares the same UPCs at Smith's stores
in different cities and flags any product whose price isn't the same everywhere.

Run from backend/:
    .venv\\Scripts\\python.exe scripts\\compare_store_prices.py
    .venv\\Scripts\\python.exe scripts\\compare_store_prices.py "eggs" "milk"
"""

import sys

import requests

from kroger_smoke_test import BASE_URL, get_token

# One zip per area. Neighboring stores usually share a price zone, so these are spread out.
AREAS = {
    "Provo": "84604",
    "Orem": "84057",
    "Salt Lake": "84111",
    "Saratoga Springs": "84045"
}
DEFAULT_TERMS = ["cheddar cheese", "eggs", "milk", "bread", "bananas", "coffee"]


def first_smiths(token, zip_code):
    resp = requests.get(
        f"{BASE_URL}/locations",
        headers={"Authorization": f"Bearer {token}"},
        params={"filter.zipCode.near": zip_code, "filter.radiusInMiles": 15, "filter.limit": 20},
        timeout=15,
    )
    resp.raise_for_status()
    for loc in resp.json().get("data", []):
        if "SMITH" in (loc.get("chain", "") + loc.get("name", "")).upper():
            return loc["locationId"]
    return None


def prices_at(token, location_id, term):
    resp = requests.get(
        f"{BASE_URL}/products",
        headers={"Authorization": f"Bearer {token}"},
        params={"filter.term": term, "filter.locationId": location_id, "filter.limit": 10},
        timeout=15,
    )
    resp.raise_for_status()
    out = {}
    for p in resp.json().get("data", []):
        item = (p.get("items") or [{}])[0]
        price = item.get("price") or {}
        if price.get("regular") is not None:
            out[p["upc"]] = (p.get("description"), price.get("regular"), price.get("promo") or None)
    return out


if __name__ == "__main__":
    terms = sys.argv[1:] or DEFAULT_TERMS
    token = get_token()

    stores = {}
    for area, zip_code in AREAS.items():
        loc = first_smiths(token, zip_code)
        if loc:
            stores[area] = loc
    print("Stores:", ", ".join(f"{a}={l}" for a, l in stores.items()), "\n")

    # results[upc] = {"name": ..., area: (regular, promo)}
    results = {}
    for term in terms:
        for area, loc in stores.items():
            for upc, (name, regular, promo) in prices_at(token, loc, term).items():
                results.setdefault(upc, {"name": name})[area] = (regular, promo)

    differing = 0
    compared = 0
    for upc, row in results.items():
        seen = {a: v for a, v in row.items() if a != "name"}
        if len(seen) < 2:
            continue
        compared += 1
        regulars = {v[0] for v in seen.values()}
        effective = {(v[1] or v[0]) for v in seen.values()}
        if len(regulars) > 1 or len(effective) > 1:
            differing += 1
            print(f"{row['name']} (UPC {upc})")
            for area, (regular, promo) in seen.items():
                sale = f"  sale ${promo}" if promo and promo != regular else ""
                print(f"   {area:<12} ${regular}{sale}")
            print()

    print(f"{differing} of {compared} products found at 2+ stores have different prices.")
