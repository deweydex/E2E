"""Compare a query built by joining strings with a parameterised query.

Run this file after setup_db.py. It does not change the database.
"""

import sqlite3
from contextlib import closing
from pathlib import Path

DATABASE_FILE = Path(__file__).parent / "vending.db"


def lookup_by_joining_strings(connection, slot_id):
    """The unsafe way: the text from the user becomes part of the SQL."""
    sql = f"SELECT item_name, stock FROM inventory WHERE slot_id = '{slot_id}'"
    print("  SQL sent to the database:", sql)
    return connection.execute(sql).fetchall()


def lookup_with_parameter(connection, slot_id):
    """The safe way: the SQL and the value travel separately."""
    sql = "SELECT item_name, stock FROM inventory WHERE slot_id = ?"
    print("  SQL sent to the database:", sql, "with value", repr(slot_id))
    return connection.execute(sql, (slot_id,)).fetchall()


with closing(sqlite3.connect(DATABASE_FILE)) as connection:
    # The first text is an ordinary slot id. The second is an attack.
    for typed_by_user in ["A1", "x' OR '1'='1"]:
        print(f"\nThe user typed: {typed_by_user}")

        print("Joined into the string:")
        print("  rows returned:", len(lookup_by_joining_strings(connection, typed_by_user)))

        print("Passed as a parameter:")
        print("  rows returned:", len(lookup_with_parameter(connection, typed_by_user)))
