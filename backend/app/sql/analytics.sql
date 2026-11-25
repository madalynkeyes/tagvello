-- Tagvello price analytics
--
-- Run the whole file in psql:
--   Get-Content backend\app\sql\analytics.sql | docker exec -i tagvello-db psql -U tagvello
-- Or open psql and paste one query at a time.
-- Pick which product and listing queries 2 and 4 look at.
-- (In psql, :product_id and :listing_id are replaced with these values.)
\set product_id 1
\set listing_id 1


-- 1. Latest price for every listing ---------------------------------------------
-- For each listing, show its most recent observation: listing_id, price and when it was observed

SELECT DISTINCT ON (listing_id)
    listing_id,
    COALESCE(promo_price, regular_price) AS price,
    observed_at
FROM price_observations
ORDER BY listing_id, observed_at DESC;


-- 2. Store comparison for one product (cheapest first) ------------------------------
-- Show the latest prices for one product in every store, order by cheapest first

WITH latest AS (
    SELECT DISTINCT ON (listing_id)
    listing_id,
    COALESCE(promo_price, regular_price) AS price,
    observed_at
    FROM price_observations
    ORDER BY listing_id, observed_at DESC
)
SELECT
    s.city,
    latest.price,
    latest.observed_at
FROM latest
JOIN listings l ON latest.listing_id = l.id
JOIN stores s   ON l.store_id = s.id
WHERE l.product_id = :product_id
ORDER BY latest.price, s.city;          -- city breaks ties so the order is stable


-- 3. Price statistics per listing -----------------------------------------------------
-- For each listing, show the lowest, highest, average price, the number of observations,
-- and the first and last time it was observed.
SELECT
    listing_id,
    min(COALESCE(promo_price, regular_price))            AS lowest,
    max(COALESCE(promo_price, regular_price))            AS highest,
    round(avg(COALESCE(promo_price, regular_price)), 2)  AS average,
    count(*)            AS observations,
    min(observed_at)                 AS first_seen,
    max(observed_at)                 AS last_seen
FROM price_observations
GROUP BY listing_id
ORDER BY listing_id;


-- 4. Price changes over time for one listing -------------------------------------------
-- For one listing, show every observation with the previous price and the change,
-- and then only the rows where the price changed.
--    4a: every observation with the previous price and the change.

SELECT
    observed_at,
    COALESCE(promo_price, regular_price) AS price,
    LAG(COALESCE(promo_price, regular_price)) OVER (ORDER BY observed_at) AS prev_price,
    COALESCE(promo_price, regular_price) 
        - LAG(COALESCE(promo_price, regular_price)) OVER (ORDER BY observed_at) AS change
FROM price_observations
WHERE listing_id = :listing_id
ORDER BY observed_at;

--    4b: only the rows where the price changed.
--    Window functions can't go in WHERE, so wrap 4a in a CTE and filter outside it.

WITH history AS (
    SELECT
    observed_at,
    COALESCE(promo_price, regular_price) AS price,
    LAG(COALESCE(promo_price, regular_price)) OVER (ORDER BY observed_at) AS prev_price,
    COALESCE(promo_price, regular_price) 
        - LAG(COALESCE(promo_price, regular_price)) OVER (ORDER BY observed_at) AS change
    FROM price_observations
    WHERE listing_id = :listing_id
    ORDER BY observed_at
)
SELECT *
FROM history
WHERE change <> 0
ORDER BY observed_at;


-- 5. "Is this a good deal?" -----------------------------------------------------------
-- For each listing, compare the latest price to its 30-day average and lowest,
-- show how far below or above average it is as a percentage, and whether it's the
-- lowest price seen in the last 30 days. Order by percentage below average (best deals first).

WITH latest AS (     -- query 1
    SELECT DISTINCT ON (listing_id)
    listing_id,
    COALESCE(promo_price, regular_price) AS price,
    observed_at
    FROM price_observations
    ORDER BY listing_id, observed_at DESC                                 
),
stats AS (
    SELECT
        listing_id,
        min(COALESCE(promo_price,regular_price))            AS low_30d,
        max(COALESCE(promo_price,regular_price))            AS high_30d,
        avg(COALESCE(promo_price,regular_price))            AS avg_raw,   -- unrounded, for the math
        round(avg(COALESCE(promo_price,regular_price)), 2)  AS avg_30d    -- rounded, for display
    FROM price_observations
    WHERE observed_at > (NOW() - INTERVAL '30 days')        -- 30 days ago
    GROUP BY listing_id
)
SELECT
    p.name,
    s.city,
    latest.price,
    stats.avg_30d,
    stats.low_30d,
    round((latest.price - stats.avg_raw) / stats.avg_raw * 100, 1)   AS pct_vs_avg,
    -- only a "low" if the price has actually varied in the last 30 days
    latest.price <= stats.low_30d AND stats.low_30d < stats.high_30d  AS is_lowest_30d
FROM latest
JOIN stats      ON latest.listing_id = stats.listing_id
JOIN listings l ON stats.listing_id = l.id
JOIN products p ON l.product_id = p.id
JOIN stores s   ON l.store_id = s.id
ORDER BY pct_vs_avg;


-- 6. Query plan for query 1 -------------------------------------------------------
--    Look for "Index Scan using price_obs_listing_time_idx" vs. "Seq Scan".

EXPLAIN ANALYZE
SELECT DISTINCT ON (listing_id)
    listing_id,
    COALESCE(promo_price, regular_price) AS price,
    observed_at
FROM price_observations
ORDER BY listing_id, observed_at DESC;                                      
