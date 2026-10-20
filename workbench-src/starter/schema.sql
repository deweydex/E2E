-- schema.sql describes the tables and the rows they start with.
-- Replace it with your own tables, then press "Reset database".

DROP TABLE IF EXISTS slots;

CREATE TABLE slots (
  slot_id     TEXT PRIMARY KEY,
  item_name   TEXT NOT NULL,
  price_cents INTEGER NOT NULL,
  stock       INTEGER NOT NULL
);

INSERT INTO slots (slot_id, item_name, price_cents, stock) VALUES
  ('A1', 'Sparkling Water', 175, 7),
  ('A2', 'Salted Crisps',   150, 5);
