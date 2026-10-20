-- schema.sql describes the tables and the rows they start with.
-- The workbench runs this whole file again when you press "Reset database".

-- Remove the old tables first, so that this file gives the same result every time it runs.
-- sales goes first because it refers to slots.
DROP TABLE IF EXISTS sales;
DROP TABLE IF EXISTS slots;

-- Each row describes one place in the machine that holds a product.
-- A CHECK rule makes the database refuse a negative price or a negative stock.
CREATE TABLE slots (
  slot_id     TEXT PRIMARY KEY,
  item_name   TEXT NOT NULL,
  price_cents INTEGER NOT NULL CHECK (price_cents >= 0),
  stock       INTEGER NOT NULL CHECK (stock >= 0)
);

-- Each row records one purchase. The price is copied into the sale, so a later price change does not alter old sales.
CREATE TABLE sales (
  sale_id     INTEGER PRIMARY KEY AUTOINCREMENT,
  slot_id     TEXT NOT NULL REFERENCES slots (slot_id),
  price_cents INTEGER NOT NULL,
  sold_at     TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO slots (slot_id, item_name, price_cents, stock) VALUES
  ('A1', 'Sparkling Water', 175, 7),
  ('A2', 'Salted Crisps',   150, 5),
  ('B1', 'Oat Biscuit',     125, 0),
  ('B2', 'Chocolate Bar',   200, 3);
