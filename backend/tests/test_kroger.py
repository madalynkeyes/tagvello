"""Tests for the Kroger adapter's JSON parsing and retry logic. No network needed."""

from decimal import Decimal

from app.kroger import KrogerClient, parse_product

SAMPLE = {
    "productId": "0007203660123",
    "upc": "0007203660123",
    "brand": "Tillamook",
    "description": "Tillamook Medium Cheddar Cheese Block",
    "categories": ["Dairy"],
    "images": [
        {"perspective": "back", "sizes": [{"size": "large", "url": "back.jpg"}]},
        {"perspective": "front", "sizes": [{"size": "small", "url": "s.jpg"}, {"size": "large", "url": "l.jpg"}]},
    ],
    "items": [{"size": "2 lb", "price": {"regular": 9.99, "promo": 0}}],
}


def test_promo_zero_means_no_sale():
    p = parse_product(SAMPLE, "70600136")
    assert p.regular_price == Decimal("9.99")
    assert p.promo_price is None
    assert p.effective_price == Decimal("9.99")


def test_real_promo_is_effective_price():
    data = {**SAMPLE, "items": [{"size": "2 lb", "price": {"regular": 9.99, "promo": 8.49}}]}
    p = parse_product(data)
    assert p.promo_price == Decimal("8.49")
    assert p.effective_price == Decimal("8.49")


def test_missing_price_is_none():
    data = {**SAMPLE, "items": [{"size": "2 lb"}]}
    p = parse_product(data)
    assert p.regular_price is None and p.promo_price is None


def test_fields_and_front_image():
    p = parse_product(SAMPLE, "70600136")
    assert p.product_id == "0007203660123"
    assert p.size == "2 lb"
    assert p.category == "Dairy"
    assert p.image_url == "l.jpg"
    assert p.location_id == "70600136"


class FakeResponse:
    def __init__(self, status, body=None, headers=None):
        self.status_code, self._body, self.headers, self.text = status, body or {}, headers or {}, ""

    def json(self):
        return self._body


class FakeSession:
    """Plays back a list of responses and counts token requests."""

    def __init__(self, gets):
        self.gets, self.token_calls = list(gets), 0

    def post(self, *a, **k):
        self.token_calls += 1
        return FakeResponse(200, {"access_token": f"t{self.token_calls}", "expires_in": 1800})

    def get(self, *a, **k):
        return self.gets.pop(0)


def test_token_is_reused():
    s = FakeSession([FakeResponse(200, {"data": []}), FakeResponse(200, {"data": []})])
    c = KrogerClient("id", "secret", session=s)
    c.search_products("eggs", "1")
    c.search_products("milk", "1")
    assert s.token_calls == 1


def test_401_gets_new_token_and_retries():
    s = FakeSession([FakeResponse(401), FakeResponse(200, {"data": {**SAMPLE}})])
    c = KrogerClient("id", "secret", session=s)
    assert c.get_product("0007203660123", "1").brand == "Tillamook"
    assert s.token_calls == 2


def test_429_backs_off_then_succeeds(monkeypatch):
    monkeypatch.setattr("app.kroger.time.sleep", lambda s: None)
    s = FakeSession([FakeResponse(429, headers={"Retry-After": "1"}), FakeResponse(200, {"data": []})])
    c = KrogerClient("id", "secret", session=s)
    assert c.search_products("eggs", "1") == []


def test_unknown_product_returns_none():
    s = FakeSession([FakeResponse(404)])
    c = KrogerClient("id", "secret", session=s)
    assert c.get_product("nope", "1") is None
