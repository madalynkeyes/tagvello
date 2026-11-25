"""Shared dependencies."""

from functools import lru_cache

from app.kroger import KrogerClient


@lru_cache
def get_kroger() -> KrogerClient:
    """One Kroger client for the whole app, so its OAuth token is reused across requests."""
    return KrogerClient.from_env()
