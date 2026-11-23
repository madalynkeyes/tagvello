-- Tagvello schema (PostgreSQL 17)
-- Run:  Get-Content backend\schema.sql | docker exec -i tagvello-db psql -U tagvello
--
-- Conventions: money is NUMERIC(10,2), times are TIMESTAMPTZ stored in UTC,
-- IDs are identity columns (users use UUIDs).
-- Tables are in foreign-key order, so each table only points at tables above it.

BEGIN;

-- 🏪 What is being sold ------------------------------------------------------

CREATE TABLE retailers (
    id          INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name        TEXT NOT NULL UNIQUE,
    website     TEXT
);

CREATE TABLE stores (
    id                    INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    retailer_id           INT  NOT NULL REFERENCES retailers (id),
    external_location_id  TEXT NOT NULL,          -- Kroger locationId, e.g. '70600136'
    name                  TEXT NOT NULL,
    address_line1         TEXT,
    city                  TEXT,
    state                 TEXT,
    postal_code           TEXT,
    UNIQUE (retailer_id, external_location_id)
);

CREATE TABLE products (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name        TEXT NOT NULL,
    brand       TEXT,
    gtin        TEXT UNIQUE,                      -- UPC; NULL allowed if a source has none
    size        TEXT,                             -- e.g. '32 oz'
    category    TEXT,
    image_url   TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);


CREATE TABLE listings (
    id                  BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_id          BIGINT NOT NULL REFERENCES products (id),  -- Tagvello's productID
    retailer_id         INT NOT NULL REFERENCES retailers (id),
    store_id            INT REFERENCES stores (id),    -- online stores can be NULL
    external_product_id TEXT NOT NULL,                 -- Kroger productID
    url                 TEXT,
    last_checked_at     TIMESTAMPTZ,                   -- NULL = never checked
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE NULLS NOT DISTINCT (retailer_id, store_id, external_product_id)
);

CREATE INDEX listings_product_id_idx ON listings (product_id);


-- 💲 Price data -----------------------------------------------------------------

CREATE TABLE ingestion_runs (
    id                BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    started_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    finished_at       TIMESTAMPTZ,
    status            TEXT NOT NULL DEFAULT 'running'
                      CHECK (status IN ('running', 'succeeded', 'failed')),
    listings_checked  INT NOT NULL DEFAULT 0,
    failures          INT NOT NULL DEFAULT 0
);

CREATE TABLE price_observations (
    id                BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    listing_id        BIGINT NOT NULL REFERENCES listings (id),
    ingestion_run_id  BIGINT NOT NULL REFERENCES ingestion_runs(id),
    regular_price     NUMERIC(10,2) NOT NULL CHECK (regular_price >0),
    promo_price       NUMERIC(10,2) CHECK (promo_price > 0),            --NULL = no sale
    observed_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(listing_id, ingestion_run_id)
);

CREATE INDEX price_obs_listing_time_idx ON price_observations (listing_id, observed_at DESC);


-- 👤 Users and intent ---------------------------------------------------------

CREATE TABLE users (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cognito_sub  TEXT NOT NULL UNIQUE,             -- stable ID from Cognito / Google sign-in
    email        TEXT NOT NULL,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE watchlist_items (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id     UUID   NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    product_id  BIGINT NOT NULL REFERENCES products (id),
    active      BOOLEAN NOT NULL DEFAULT true,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (user_id, product_id)                  -- a user watches a product once
);

CREATE TABLE alert_rules (
    id                 BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    watchlist_item_id  BIGINT NOT NULL REFERENCES watchlist_items (id) ON DELETE CASCADE,
    target_price       NUMERIC(10,2) NOT NULL CHECK (target_price > 0),
    enabled            BOOLEAN NOT NULL DEFAULT true,
    created_at         TIMESTAMPTZ NOT NULL DEFAULT now()
);


-- 🔔 Alert output ---------------------------------------------------------------

-- 📱 device_tokens is for the future mobile app, so it's left out of the MVP.

CREATE TABLE notification_events(
    id                        BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY, 
    alert_rule_id             BIGINT NOT NULL REFERENCES alert_rules (id) ON DELETE CASCADE,
    triggering_observation_id BIGINT NOT NULL REFERENCES price_observations (id),
    status                    TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending','sent','failed')),
    error_message             TEXT,                               -- why it failed for debugging
    created_at                TIMESTAMPTZ NOT NULL DEFAULT now(),
    sent_at                   TIMESTAMPTZ,                        -- NULL until sent
    UNIQUE (alert_rule_id, triggering_observation_id),
    CHECK ((status = 'sent') = (sent_at IS NOT NULL))             -- make sure sent rows always have a time
);


COMMIT;
