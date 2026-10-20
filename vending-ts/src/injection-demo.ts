// Compare a query built by joining strings with a parameterised query.
//
// Run this file after setup-db.ts. It does not change the database.

import path from "node:path";
import { DatabaseSync } from "node:sqlite";

const DATABASE_FILE = path.join(import.meta.dirname, "..", "vending.db");
const database = new DatabaseSync(DATABASE_FILE);

// The unsafe way: the text from the user becomes part of the SQL.
function lookupByJoiningStrings(slotId: string): unknown[] {
  const sql = `SELECT item_name, stock FROM inventory WHERE slot_id = '${slotId}'`;
  console.log("  SQL sent to the database:", sql);
  return database.prepare(sql).all();
}

// The safe way: the SQL and the value travel separately.
function lookupWithParameter(slotId: string): unknown[] {
  const sql = "SELECT item_name, stock FROM inventory WHERE slot_id = ?";
  console.log("  SQL sent to the database:", sql, "with value", JSON.stringify(slotId));
  return database.prepare(sql).all(slotId);
}

// The first text is an ordinary slot id. The second is an attack.
for (const typedByUser of ["A1", "x' OR '1'='1"]) {
  console.log(`\nThe user typed: ${typedByUser}`);

  console.log("Joined into the string:");
  console.log("  rows returned:", lookupByJoiningStrings(typedByUser).length);

  console.log("Passed as a parameter:");
  console.log("  rows returned:", lookupWithParameter(typedByUser).length);
}

database.close();
