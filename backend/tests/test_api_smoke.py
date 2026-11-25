"""Quick checks that the app starts and the finished endpoints respond.

Needs the local database running (docker compose up -d) with schema.sql and seed.sql loaded.
Run from backend/:  .venv\\Scripts\\python.exe -m pytest tests
"""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_unknown_product_is_404():
    assert client.get("/products/999999/stores").status_code == 404
