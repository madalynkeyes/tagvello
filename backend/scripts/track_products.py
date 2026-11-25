"""Seed the products and listings that the worker will track.

This decides what products to track by searching for a few terms at one store,
and then inserting the first result with a UPC and price into the products table,
and a listing for each store. Run this once or whenever you want to add more products to track.

"""
import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row

from app.catalog import track_product
from app.kroger import KrogerClient

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

PROVO_LOCATION_ID = "70600136"   # search here; track_product adds every store

SEARCH_TERMS = [
    "cheddar cheese", "eggs", "milk", "bread", "bananas",
    "tomatoes", "cereal", "butter", "ground beef", "paper towels",
]


def main():
    client = KrogerClient.from_env()

    with psycopg.connect(os.environ["DATABASE_URL"], row_factory=dict_row) as conn:
        for term in SEARCH_TERMS:
            for product in client.search_products(term, PROVO_LOCATION_ID):
                if not product.upc or product.regular_price is None:
                    print(f"  skipping {product.description} (no UPC or price)")
                    continue
                product_id = track_product(conn, product)
                print(f"Tracking: {product.description} (product {product_id})")
                break
            else:
                print(f"No trackable product found for '{term}'")


if __name__ == "__main__":
    main()