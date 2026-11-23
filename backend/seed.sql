-- Starting data: Smith's and the four tracked stores.
-- Run after schema.sql:
--   Get-Content backend\seed.sql | docker exec -i tagvello-db psql -U tagvello

INSERT INTO retailers (name, website)
VALUES ('Smith''s', 'https://www.smithsfoodanddrug.com')
ON CONFLICT (name) DO NOTHING;

INSERT INTO stores (retailer_id, external_location_id, name, city, state)
SELECT r.id, s.loc, s.name, s.city, 'UT'
FROM retailers r
CROSS JOIN (VALUES
    ('70600136', 'Provo Smith''s',            'Provo'),
    ('70600144', 'Orem Smith''s',             'Orem'),
    ('70600094', 'Salt Lake Smith''s',        'Salt Lake City'),
    ('70600207', 'Saratoga Springs Smith''s', 'Saratoga Springs')
) AS s (loc, name, city)
WHERE r.name = 'Smith''s'
ON CONFLICT (retailer_id, external_location_id) DO NOTHING;
