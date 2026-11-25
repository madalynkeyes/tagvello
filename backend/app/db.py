"""Database connection for each request."""

import os
from collections.abc import Iterator

import psycopg
from psycopg.rows import dict_row


def get_conn() -> Iterator[psycopg.Connection]:
    """FastAPI dependency: one connection per request.

    Rows come back as dicts (row["price"]) instead of tuples (row[1]), which maps
    straight onto the response models. The `with` block commits when the request
    succeeds and rolls back if the endpoint raises an error.

    (On AWS Lambda this becomes one connection reused across requests.)
    """
    with psycopg.connect(os.environ["DATABASE_URL"], row_factory=dict_row) as conn:
        yield conn
