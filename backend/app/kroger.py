"""
Kroger Public API adapter.

Turns Kroger's JSON into small, typed records the rest of Tagvello can use,
and hides the OAuth token, retries, and rate-limit handling.

    client = KrogerClient.from_env()
    for p in client.search_products("cheddar", location_id="70600136"):
        print(p.description, p.regular_price, p.promo_price)
"""

from __future__ import annotations

import base64
import os
import time
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

import requests

DEFAULT_BASE_URL = "https://api.kroger.com/v1"
PRODUCT_SCOPE = "product.compact"
RETRY_STATUSES = {429, 500, 502, 503, 504}


class KrogerError(RuntimeError):
    """The Kroger API returned an error we couldn't recover from."""


@dataclass(frozen=True)
class KrogerProduct:
    """One product as priced at one store."""

    product_id: str                 # Kroger productId -> listings.external_product_id
    upc: str | None                 # -> products.gtin
    brand: str | None
    description: str                # -> products.name
    size: str | None
    category: str | None
    image_url: str | None
    regular_price: Decimal | None   # None = no price at this store (often out of stock)
    promo_price: Decimal | None     # None = no sale (Kroger sends 0 for "no promo")
    location_id: str | None

    @property
    def effective_price(self) -> Decimal | None:
        """What you'd actually pay: the sale price if there is one."""
        return self.promo_price or self.regular_price


@dataclass(frozen=True)
class KrogerLocation:
    location_id: str
    name: str
    chain: str | None
    address_line1: str | None
    city: str | None
    state: str | None
    postal_code: str | None


# --- JSON -> records ---------------------------------------------------------


def _money(value: Any) -> Decimal | None:
    """Kroger sends prices as JSON numbers. Go through str() so 8.49 stays exactly 8.49,
    and treat 0 or missing as 'no price'."""
    if value is None:
        return None
    amount = Decimal(str(value)).quantize(Decimal("0.01"))
    return amount if amount > 0 else None


def _image_url(images: list[dict]) -> str | None:
    """Prefer the front photo, in the largest size offered."""
    if not images:
        return None
    front = next((i for i in images if i.get("perspective") == "front"), images[0])
    order = ["xlarge", "large", "medium", "small", "thumbnail"]
    sizes = sorted(front.get("sizes", []), key=lambda s: order.index(s["size"]) if s.get("size") in order else len(order))
    return sizes[0].get("url") if sizes else None


def parse_product(data: dict, location_id: str | None = None) -> KrogerProduct:
    item = (data.get("items") or [{}])[0]
    price = item.get("price") or {}
    categories = data.get("categories") or []
    return KrogerProduct(
        product_id=str(data["productId"]),
        upc=data.get("upc"),
        brand=data.get("brand"),
        description=data.get("description") or "",
        size=item.get("size"),
        category=categories[0] if categories else None,
        image_url=_image_url(data.get("images") or []),
        regular_price=_money(price.get("regular")),
        promo_price=_money(price.get("promo")),
        location_id=location_id,
    )


def parse_location(data: dict) -> KrogerLocation:
    addr = data.get("address") or {}
    return KrogerLocation(
        location_id=str(data["locationId"]),
        name=data.get("name") or "",
        chain=data.get("chain"),
        address_line1=addr.get("addressLine1"),
        city=addr.get("city"),
        state=addr.get("state"),
        postal_code=addr.get("zipCode"),
    )


# --- HTTP client -------------------------------------------------------------


class KrogerClient:
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        base_url: str = DEFAULT_BASE_URL,
        session: requests.Session | None = None,
        max_retries: int = 3,
        timeout: float = 15,
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = base_url.rstrip("/")
        self.session = session or requests.Session()
        self.max_retries = max_retries
        self.timeout = timeout
        self._token: str | None = None
        self._token_expires_at = 0.0

    @classmethod
    def from_env(cls) -> "KrogerClient":
        client_id = os.getenv("KROGER_CLIENT_ID")
        client_secret = os.getenv("KROGER_CLIENT_SECRET")
        if not client_id or not client_secret:
            raise KrogerError("KROGER_CLIENT_ID and KROGER_CLIENT_SECRET must be set")
        return cls(client_id, client_secret, os.getenv("KROGER_BASE_URL", DEFAULT_BASE_URL))

    # OAuth 2.0 client credentials. Tokens last ~30 minutes, so reuse one until
    # a minute before it expires instead of asking for a new one on every call.
    def _get_token(self) -> str:
        if self._token and time.time() < self._token_expires_at - 60:
            return self._token
        basic = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
        resp = self.session.post(
            f"{self.base_url}/connect/oauth2/token",
            headers={"Authorization": f"Basic {basic}"},
            data={"grant_type": "client_credentials", "scope": PRODUCT_SCOPE},
            timeout=self.timeout,
        )
        if resp.status_code != 200:
            raise KrogerError(f"Token request failed ({resp.status_code}): {resp.text[:200]}")
        body = resp.json()
        self._token = body["access_token"]
        self._token_expires_at = time.time() + int(body.get("expires_in", 1800))
        return self._token

    def _get(self, path: str, params: dict) -> dict:
        """GET with retries: back off on 429/5xx, and get a fresh token once on 401."""
        refreshed = False
        for attempt in range(self.max_retries + 1):
            resp = self.session.get(
                f"{self.base_url}{path}",
                headers={"Authorization": f"Bearer {self._get_token()}", "Accept": "application/json"},
                params=params,
                timeout=self.timeout,
            )
            if resp.status_code == 200:
                return resp.json()
            if resp.status_code == 401 and not refreshed:
                self._token = None
                refreshed = True
                continue
            if resp.status_code in RETRY_STATUSES and attempt < self.max_retries:
                retry_after = resp.headers.get("Retry-After")
                time.sleep(float(retry_after) if retry_after and retry_after.isdigit() else 2**attempt)
                continue
            if resp.status_code == 404:
                return {}
            raise KrogerError(f"GET {path} failed ({resp.status_code}): {resp.text[:200]}")
        raise KrogerError(f"GET {path} failed after {self.max_retries} retries")

    # --- public methods -------------------------------------------------------

    def find_locations(self, zip_code: str, radius_miles: int = 10, limit: int = 10) -> list[KrogerLocation]:
        body = self._get(
            "/locations",
            {"filter.zipCode.near": zip_code, "filter.radiusInMiles": radius_miles, "filter.limit": limit},
        )
        return [parse_location(d) for d in body.get("data", [])]

    def search_products(self, term: str, location_id: str, limit: int = 10) -> list[KrogerProduct]:
        """Keyword search at one store. Prices only come back when location_id is given."""
        body = self._get(
            "/products",
            {"filter.term": term, "filter.locationId": location_id, "filter.limit": limit},
        )
        return [parse_product(d, location_id) for d in body.get("data", [])]

    def get_product(self, product_id: str, location_id: str) -> KrogerProduct | None:
        """Current price of one product at one store. This is what the worker calls per listing."""
        body = self._get(f"/products/{product_id}", {"filter.locationId": location_id})
        data = body.get("data")
        return parse_product(data, location_id) if data else None
