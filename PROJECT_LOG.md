# Project Log

A record of work on Tagvello: the date, what I did, and how long it took.

| Date | What I Did | Hours |
|------|------------|------:|
| 11/17/2026 | Came up with ideas and planned the project: chose the price-data sources (Kroger, Best Buy), compared AWS and Railway costs, set up the GitHub repo, README, and project log | 1 |
| 11/19/2026 | Initial design: wrote the project summary, "how it's different" table, and goals; designed the system diagram and ERD on a whiteboard (user path vs. background path, table groups and relationships); made the UI mockup; planned daily goals through Dec 10 | 2 |
| 11/23/2026 | Set up the project structure and Python venv; got a Kroger API key and tested the token, Locations, and Products APIs; compared prices across Smith's stores and chose Provo, Orem, Salt Lake, and Saratoga Springs; set up Postgres in Docker; wrote the schema (listings, price_observations, and notification_events by hand) and seed data, and tested the constraints | 2 |
| 11/25/2026 | Added the Kroger adapter (token caching, retries, JSON parsing) with tests; wrote track_products.py to seed 10 products and 40 listings with idempotent upserts; wrote the ingestion worker (ingest.py) with per-listing transactions and run tracking; set up a daily Windows Task Scheduler job with logging so prices collect automatically; wrote the SQL analytics queries (latest price, store comparison, price stats, price changes with LAG, 30-day deal score, EXPLAIN ANALYZE); started the FastAPI backend: price history, deal stats, and watchlist list/add endpoints, with the product upserts moved into a shared catalog.py | 5.5 |
| **Total** | | **10.5** |
