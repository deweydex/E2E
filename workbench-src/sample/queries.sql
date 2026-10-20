-- queries.sql holds every question the server may ask the database.
-- Each query starts with a comment of the form "-- name: something".
-- A word with a colon in front, such as :slot, is a parameter.
-- The server fills in each parameter safely, so a visitor cannot change the SQL itself.

-- name: list_slots
SELECT slot_id, item_name, price_cents, stock
FROM slots
ORDER BY slot_id;

-- name: get_slot
SELECT slot_id, item_name, price_cents, stock
FROM slots
WHERE slot_id = :slot;

-- name: buy_slot
-- This query has two statements that succeed or fail together. Both check that stock is above zero,
-- so a sold-out slot records no sale and loses no stock.
-- The INSERT comes first on purpose. If the UPDATE ran first, the last item would leave stock at zero,
-- and the INSERT would then find no stock and record no sale.
INSERT INTO sales (slot_id, price_cents)
SELECT slot_id, price_cents FROM slots WHERE slot_id = :slot AND stock > 0;
UPDATE slots SET stock = stock - 1 WHERE slot_id = :slot AND stock > 0;

-- name: restock_slot
-- The check on :amount stops a negative number from removing stock.
UPDATE slots SET stock = stock + :amount WHERE slot_id = :slot AND :amount > 0;

-- name: list_sales
SELECT sales.sale_id, slots.item_name, sales.price_cents, sales.sold_at
FROM sales
JOIN slots ON slots.slot_id = sales.slot_id
ORDER BY sales.sale_id DESC
LIMIT 20;
