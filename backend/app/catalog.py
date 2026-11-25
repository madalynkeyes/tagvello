"""Saving Kroger products into Tagvello's catalog. Shared by the API and scripts."""

import psycopg

from app.kroger import KrogerProduct


def track_product(conn: psycopg.Connection, product: KrogerProduct) -> int:
    """Upsert a product and a listing for it at every Smith's store.

    Runs inside the caller's transaction (the caller commits).
    Expects dict rows (row_factory=dict_row). Returns the Tagvello product id.
    """
    if not product.upc:
        raise ValueError(f"Can't track a product with no UPC: {product.description}")

    retailer_id = conn.execute(
        "SELECT id FROM retailers WHERE name = %s", ("Smith's",)
    ).fetchone()["id"]

    store_ids = [
        row["id"]
        for row in conn.execute(
            "SELECT id FROM stores WHERE retailer_id = %s", (retailer_id,)
        ).fetchall()
    ]

    product_id = conn.execute(
        """
        INSERT INTO products (name, brand, gtin, size, category, image_url)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (gtin) DO UPDATE
        SET name = EXCLUDED.name, image_url = EXCLUDED.image_url
        RETURNING id
        """,
        (product.description, product.brand, product.upc,
         product.size, product.category, product.image_url),
    ).fetchone()["id"]

    for store_id in store_ids:
        conn.execute(
            """
            INSERT INTO listings (product_id, retailer_id, store_id, external_product_id)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (retailer_id, store_id, external_product_id) DO NOTHING
            """,
            (product_id, retailer_id, store_id, product.product_id),
        )

    return product_id