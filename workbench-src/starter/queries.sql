-- queries.sql holds every question the server may ask the database.
-- Each query starts with a comment of the form "-- name: something".
-- A word with a colon in front, such as :slot, is a parameter.

-- name: list_slots
SELECT slot_id, item_name, price_cents, stock
FROM slots
ORDER BY slot_id;
