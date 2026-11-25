"""Who is making the request.

TEMPORARY: until Cognito is set up (Nov 30), every request is the same local
"dev" user. Endpoints already depend on get_current_user, so switching to real
Google sign-in later only changes this file: it will read the Cognito JWT from
the Authorization header and use its `sub` claim instead of DEV_USER_SUB.
"""

import psycopg
from fastapi import Depends

from app.db import get_conn

DEV_USER_SUB = "dev-user"
DEV_USER_EMAIL = "dev@tagvello.local"


def get_current_user(conn: psycopg.Connection = Depends(get_conn)) -> dict:
    """Return the signed-in user's row, creating it on first sign-in."""
    return conn.execute(
        """
        INSERT INTO users (cognito_sub, email)
        VALUES (%s, %s)
        ON CONFLICT (cognito_sub) DO UPDATE SET email = EXCLUDED.email
        RETURNING id, email
        """,
        (DEV_USER_SUB, DEV_USER_EMAIL),
    ).fetchone()
