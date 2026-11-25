"""Seed the products and listings that the worker will track."""

import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv

from app.kroger import KrogerClient

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

SEARCH_TERMS = [
    "cheddar cheese", "eggs", "milk", "bread", "bananas",
    "tomatoes", "cereal", "butter", "ground beef", "paper towels",
]


def main():
    client = KrogerClient.from_env()

    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        # 1: get Smith's retailer_id
        row = conn.execute(
            "SELECT id FROM retailers WHERE name = %s",("Smith's",)
        ).fetchone()
        retailer_id = row[0]
        
        # 2: get all stores as (id, external_location_id) rows
        stores = conn.execute(
            "SELECT id, external_location_id FROM stores WHERE retailer_id = %s",(retailer_id,)
        ).fetchall()

        # 3: pick the Provo store's external_location_id to search with
        provo_location_id = None
        for _, external_location_id in stores:
            if external_location_id == "70600136":
                provo_location_id = external_location_id
                break

        for term in SEARCH_TERMS:
            results = client.search_products(term, provo_location_id)
            # 4: choose the first result with a upc and a regular_price
            for product in results:
                if product.upc and product.regular_price is None:
                    # (skip the term and print a message if there isn't one)
                    print("Skipping product with no price:", product.description)
                    product_id = None
                    continue
                else:
                    # 5: upsert the product, RETURNING id
                    product_row = conn.execute(
                        """
                        INSERT INTO products (name, brand, gtin, size, category, image_url) 
                        VALUES (%s,%s,%s,%s,%s,%s) 
                        ON CONFLICT (gtin) DO UPDATE 
                        SET name = EXCLUDED.name, image_url = EXCLUDED.image_url 
                        RETURNING id;
                        """,(product.description, product.brand, product.upc, product.size, product.category, product.image_url,)
                    ).fetchone()
                    product_id = product_row[0]
                    created = 0
                    for store_id, external_location_id in stores:
                        if product_id is not None:
                            # 6: for each store, upsert a listing (product_id, retailer_id, store_id, external_product_id)
                            cur = conn.execute(
                                """
                                INSERT INTO listings (product_id, retailer_id, store_id, external_product_id) 
                                VALUES (%s,%s,%s,%s) 
                                ON CONFLICT (store_id, retailer_id, external_product_id) DO NOTHING;
                                """,(product_id, retailer_id, store_id, product.product_id,)
                            )
                            created += cur.rowcount
                    print(f"Upserted product {product.description} with {created} listings.")
                    break # only track one product per search term
            print(f"Tracking: {product.description}")


if __name__ == "__main__":
    main()