"""Record the current price of every listing. Run once a day.

Based on the products and listings already in the database (populated by track_products.py),
the script calls Kroger's API to get the current price of each listing, and inserts a row into
price_observations. It also updates the listing's last_checked_at timestamp, and records 
the run in ingestion_runs with the number of listings checked and the number of failures. 

"""

import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv

from app.kroger import KrogerClient

load_dotenv(Path(__file__).resolve().parents[2] / ".env")


def main():
    client = KrogerClient.from_env()

    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        # 1: insert an ingestion_runs row, RETURNING id, then commit
        run_id = conn.execute(
            """
            INSERT INTO ingestion_runs DEFAULT VALUES RETURNING id;"""
        ).fetchone()[0]
        conn.commit()

        # 2: select (listing id, external_product_id, store's external_location_id)
        listings = conn.execute(
            """
            SELECT l.id, l.external_product_id, s.external_location_id
            FROM listings l
            LEFT JOIN stores s ON l.store_id = s.id;"""
        ).fetchall()

        checked = failures = 0
        for listing_id, external_product_id, location_id in listings:
            try:
                # this makes one api call per listing
                product = client.get_product(external_product_id, location_id)

                if product is None or product.regular_price is None:
                    failures += 1          # not sold here or out of stock
                    continue
                # 3: insert into price_observations
                conn.execute(
                    """
                    INSERT INTO price_observations (listing_id, ingestion_run_id, regular_price, promo_price)
                    VALUES (%s,%s,%s,%s);""",(listing_id,run_id,product.regular_price,product.promo_price,)
                )
                
                # 4: set this listing's last_checked_at = now()
                conn.execute(
                    """
                    UPDATE listings
                    SET last_checked_at = NOW()
                    WHERE id = %s;""", (listing_id,)
                )
                conn.commit()
                checked += 1
            except Exception as e:
                conn.rollback()
                failures += 1
                print(f"Listing {listing_id} failed: {e}")
                print(f"Listing {listing_id} failed: no price at store {location_id}")
                
        # 5: update the run: finished_at = now(), listings_checked,
        #         failures, and status ('succeeded' if checked > 0 else 'failed')
        conn.execute(
            """
            UPDATE ingestion_runs
            SET finished_at = NOW(), listings_checked = %s, failures = %s,
                status = CASE WHEN %s > 0 THEN 'succeeded' ELSE 'failed' END
            WHERE id = %s;""",(checked,failures,checked,run_id,)
        )
        
        conn.commit()
        print(f"Run {run_id}: {checked} prices saved, {failures} failures")


if __name__ == "__main__":
    main()