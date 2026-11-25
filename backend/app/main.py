"""
Tagvello API.

Run locally from backend/ (with the venv active and Docker running):
    .venv\\Scripts\\python.exe -m uvicorn app.main:app --reload

Then open http://127.0.0.1:8000/docs to try every endpoint in the browser.
"""

from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

from fastapi import FastAPI  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402

from app.routers import alerts, products, watchlist  # noqa: E402

app = FastAPI(
    title="Tagvello API",
    description="Track grocery prices across Smith's stores and get alerted when they drop.",
    version="0.1.0",
)

# Lets the React site (Vite runs on port 5173) call this API from the browser.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products.router)
app.include_router(watchlist.router)
app.include_router(alerts.router)


@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok"}
