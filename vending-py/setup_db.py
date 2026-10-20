"""Create the vending machine database and fill it with a few snacks.

Run this file once before you start the server.
Running it again resets the machine to its starting state.
"""

import sqlite3
from contextlib import closing
from pathlib import Path

# The database is one ordinary file that sits beside this script.
# Path(__file__).parent is the folder that holds this script, so the file
# ends up in the same place no matter where you run the script from.
DATABASE_FILE = Path(__file__).parent / "vending.db"

# The schema describes the shape of our data: one table with four columns.
# The comments after the double dashes are SQL comments.
SCHEMA = """
DROP TABLE IF EXISTS inventory;

CREATE TABLE inventory (
    slot_id     TEXT    PRIMARY KEY,                           -- identifies one slot, for example A1
    item_name   TEXT    NOT NULL,                              -- every slot must have a name
    price_cents INTEGER NOT NULL CHECK (price_cents >= 0),     -- whole cents, never decimals
    stock       INTEGER NOT NULL CHECK (stock >= 0)            -- the database refuses negative stock
);
"""

# Each tuple is one row: (slot_id, item_name, price_cents, stock).
# The Oat Biscuits start with no stock so that we can test a sold-out slot.
STARTING_STOCK = [
    ("A1", "Sparkling Water", 175, 8),
    ("A2", "Salted Peanuts", 125, 5),
    ("B1", "Chocolate Bar", 200, 3),
    ("B2", "Oat Biscuits", 150, 0),
]

# closing() makes sure that the connection is closed when the block ends.
with closing(sqlite3.connect(DATABASE_FILE)) as connection:
    # "with connection" groups the work into one transaction. If every
    # statement succeeds, the changes are committed together. If one fails,
    # the changes since the last commit are rolled back.
    with connection:
        # executescript runs several SQL statements in one call. It commits
        # anything that came before it, so creating the table is its own step.
        connection.executescript(SCHEMA)

        # The question marks are placeholders. The values travel to the
        # database separately from the SQL text. The four inserts that follow
        # belong to one transaction, so either all of them are stored or none.
        connection.executemany(
            "INSERT INTO inventory (slot_id, item_name, price_cents, stock) VALUES (?, ?, ?, ?)",
            STARTING_STOCK,
        )

    # Read the rows back so that we can see what was stored.
    for row in connection.execute(
        "SELECT slot_id, item_name, price_cents, stock FROM inventory ORDER BY slot_id"
    ):
        print(row)
