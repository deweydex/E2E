// Create the vending machine database and fill it with a few snacks.
//
// Run this file once before you start the server.
// Running it again resets the machine to its starting state.

import path from "node:path";
import { DatabaseSync } from "node:sqlite";

// The database is one ordinary file in the project folder.
// import.meta.dirname is the folder that holds this file, which is src,
// so ".." leads to the project folder above it.
const DATABASE_FILE = path.join(import.meta.dirname, "..", "vending.db");

// The schema describes the shape of our data: one table with four columns.
// The comments after the double dashes are SQL comments.
const SCHEMA = `
DROP TABLE IF EXISTS inventory;

CREATE TABLE inventory (
    slot_id     TEXT    PRIMARY KEY,                           -- identifies one slot, for example A1
    item_name   TEXT    NOT NULL,                              -- every slot must have a name
    price_cents INTEGER NOT NULL CHECK (price_cents >= 0),     -- whole cents, never decimals
    stock       INTEGER NOT NULL CHECK (stock >= 0)            -- the database refuses negative stock
);
`;

// Each entry is one row: [slot_id, item_name, price_cents, stock].
// The type after the colon says "a list of lists, each holding two strings
// and two numbers". The Oat Biscuits start with no stock so that we can test
// a sold-out slot.
const STARTING_STOCK: [string, string, number, number][] = [
  ["A1", "Sparkling Water", 175, 8],
  ["A2", "Salted Peanuts", 125, 5],
  ["B1", "Chocolate Bar", 200, 3],
  ["B2", "Oat Biscuits", 150, 0],
];

// Opening the database opens the file, and creates it if it does not exist.
const database = new DatabaseSync(DATABASE_FILE);

// A transaction groups the work: either all of it happens or none of it does.
database.exec("BEGIN");
database.exec(SCHEMA);

// A prepared statement is SQL that the database reads once and can run many
// times. The question marks are placeholders, and the values travel to the
// database separately from the SQL text.
const insertSlot = database.prepare(
  "INSERT INTO inventory (slot_id, item_name, price_cents, stock) VALUES (?, ?, ?, ?)",
);
for (const slotRow of STARTING_STOCK) {
  // The three dots spread the four values of the row into four arguments.
  insertSlot.run(...slotRow);
}
database.exec("COMMIT");

// Read the rows back so that we can see what was stored.
const storedRows = database
  .prepare("SELECT slot_id, item_name, price_cents, stock FROM inventory ORDER BY slot_id")
  .all();
for (const storedRow of storedRows) {
  console.log(Object.values(storedRow));
}

database.close();
