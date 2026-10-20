"""A small web server that sells snacks from a SQLite database.

The file has four layers, from the bottom of the program to the top:
  1. The data layer talks to the database. It knows nothing about HTTP.
  2. The route layer connects URLs to data functions and checks the input.
  3. The HTTP layer reads requests and writes responses.
  4. The last lines start the server.
"""

import json
import re
import sqlite3
from contextlib import closing
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

# --- Settings ----------------------------------------------------------------

# 127.0.0.1 means "this computer", so only programs on your own machine can connect.
HOST = "127.0.0.1"

# The port decides which program on this computer receives the request.
PORT = 8000

DATABASE_FILE = Path(__file__).parent / "vending.db"
PUBLIC_FOLDER = Path(__file__).parent / "public"

# The only files that the server will send. Each URL path maps to a file name
# and a Content-Type. A fixed list stops visitors from asking for other files,
# such as server.py or vending.db, by typing a path like /../server.py.
STATIC_FILES = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/style.css": ("style.css", "text/css; charset=utf-8"),
    "/app.js": ("app.js", "text/javascript; charset=utf-8"),
}

# A valid slot id is one capital letter followed by one digit, such as A1 or B2.
SLOT_ID_PATTERN = re.compile(r"[A-Z][0-9]")


# --- Errors ------------------------------------------------------------------
# The data layer reports problems by raising these exceptions. Each name
# describes a problem in the language of the vending machine, and the HTTP
# layer decides which status code each problem deserves.


class BadRequest(Exception):
    """The client sent something we cannot make sense of."""


class NoSuchSlot(Exception):
    """The slot id is well formed, but no such slot exists."""


class SoldOut(Exception):
    """The slot exists, but it has no stock left."""


# --- Data layer --------------------------------------------------------------
# These functions are the only place where the program talks to the database.


def open_connection():
    """Open a new connection to the database file."""
    connection = sqlite3.connect(DATABASE_FILE)
    # With sqlite3.Row we can read a column by name, as in row["stock"],
    # and not only by position.
    connection.row_factory = sqlite3.Row
    return connection


def find_slot(connection, slot_id):
    """Return one slot as a dictionary, or None if there is no such slot."""
    # The ? is a placeholder. The value travels separately from the SQL text,
    # so a visitor can never change what the SQL means (SQL injection).
    # A tuple with one item needs the trailing comma.
    row = connection.execute(
        "SELECT slot_id, item_name, price_cents, stock FROM inventory WHERE slot_id = ?",
        (slot_id,),
    ).fetchone()
    return dict(row) if row else None


def get_all_slots():
    """Return every slot as a list of dictionaries."""
    with closing(open_connection()) as connection:
        # Without ORDER BY, SQL promises no particular order for the rows.
        rows = connection.execute(
            "SELECT slot_id, item_name, price_cents, stock FROM inventory ORDER BY slot_id"
        ).fetchall()
    return [dict(row) for row in rows]


def get_slot(slot_id):
    """Return one slot, or raise NoSuchSlot."""
    with closing(open_connection()) as connection:
        slot = find_slot(connection, slot_id)
    if slot is None:
        raise NoSuchSlot(f"No slot called {slot_id}.")
    return slot


def buy_slot(slot_id):
    """Take one item from a slot and return the updated slot."""
    with closing(open_connection()) as connection:
        # "with connection" is one transaction. The changes are committed if
        # the block ends normally and rolled back if an exception escapes.
        with connection:
            # One statement checks the stock and changes it. If two buyers
            # arrive at the same moment, the database handles them one after
            # the other, so they cannot both take the last item.
            update_result = connection.execute(
                "UPDATE inventory SET stock = stock - 1 WHERE slot_id = ? AND stock > 0",
                (slot_id,),
            )
            # Read the slot inside the same transaction, so that the numbers
            # we report agree with the change we just made.
            slot = find_slot(connection, slot_id)

    # rowcount is the number of rows that the UPDATE changed.
    if slot is None:
        raise NoSuchSlot(f"No slot called {slot_id}.")
    if update_result.rowcount == 0:
        raise SoldOut(f"{slot['item_name']} is sold out.")
    return slot


# --- Route layer -------------------------------------------------------------
# A handler connects one URL to one data function. It checks the input, calls
# the data layer and returns data. It contains no SQL and no HTTP details.


def validate_slot_id(raw_slot_id):
    """Tidy up a slot id from the URL and check that it has the right shape."""
    # upper() lets a visitor type a1 and mean A1.
    slot_id = raw_slot_id.upper()
    if not SLOT_ID_PATTERN.fullmatch(slot_id):
        raise BadRequest("Slot ids look like A1 or B2.")
    return slot_id


def handle_list_slots():
    return get_all_slots()


def handle_show_slot(raw_slot_id):
    return get_slot(validate_slot_id(raw_slot_id))


def handle_buy_slot(raw_slot_id):
    return buy_slot(validate_slot_id(raw_slot_id))


# The route table is the API written as data. Each row holds an HTTP method, a
# pattern for the URL path, and the handler for that route. In a pattern,
# ([^/]+) captures the text between two slashes, and the captured text is
# passed to the handler as an argument.
ROUTES = [
    ("GET", re.compile(r"/api/slots"), handle_list_slots),
    ("GET", re.compile(r"/api/slots/([^/]+)"), handle_show_slot),
    ("POST", re.compile(r"/api/slots/([^/]+)/buy"), handle_buy_slot),
]


# --- HTTP layer --------------------------------------------------------------


class VendingRequestHandler(BaseHTTPRequestHandler):
    """Python creates one of these objects for every request that arrives."""

    # BaseHTTPRequestHandler calls do_GET for GET requests and do_POST for
    # POST requests. We send both to one method of our own.
    def do_GET(self):
        self.answer_request("GET")

    def do_POST(self):
        self.answer_request("POST")

    def answer_request(self, http_method):
        # self.path includes any query string, so we keep only the path.
        url_path = urlsplit(self.path).path

        try:
            # First, is the visitor asking for one of our page files?
            if http_method == "GET" and url_path in STATIC_FILES:
                self.send_static_file(url_path)
                return

            # Otherwise look for a matching route. The first match wins.
            for route_method, path_pattern, handler in ROUTES:
                path_match = path_pattern.fullmatch(url_path)
                if route_method == http_method and path_match:
                    # groups() holds the captured text, such as "A1".
                    self.send_json(200, handler(*path_match.groups()))
                    return

            # Nothing matched.
            self.send_json(404, {"error": "No such route."})

        # These lines turn the exceptions of the data layer into status codes.
        except BadRequest as error:
            self.send_json(400, {"error": str(error)})
        except NoSuchSlot as error:
            self.send_json(404, {"error": str(error)})
        except SoldOut as error:
            self.send_json(409, {"error": str(error)})
        except Exception as error:
            # Anything else is a bug in our program. We print the details for
            # the developer and tell the visitor very little.
            print("Unexpected error:", repr(error))
            self.send_json(500, {"error": "Something went wrong on the server."})

    def send_static_file(self, url_path):
        file_name, content_type = STATIC_FILES[url_path]
        body = (PUBLIC_FOLDER / file_name).read_bytes()
        self.send_body(200, content_type, body)

    def send_json(self, status_code, data):
        # json.dumps turns the data into text, and encode turns the text into
        # bytes, because a network carries bytes and not characters.
        body = json.dumps(data).encode("utf-8")
        self.send_body(status_code, "application/json; charset=utf-8", body)

    def send_body(self, status_code, content_type, body):
        # HTTP requires this order: status line, headers, a blank line, body.
        self.send_response(status_code)
        self.send_header("Content-Type", content_type)  # how to read the body
        self.send_header("Content-Length", str(len(body)))  # how many bytes follow
        self.send_header("Cache-Control", "no-store")  # always ask again while we develop
        self.end_headers()  # writes the blank line
        self.wfile.write(body)


# This block runs only when you start this file directly. It does not run when
# another file imports server.py to reuse the data functions.
if __name__ == "__main__":
    web_server = ThreadingHTTPServer((HOST, PORT), VendingRequestHandler)
    print(f"Vending machine running at http://{HOST}:{PORT}  (press Ctrl+C to stop)")
    try:
        # Wait for requests and answer each one in its own thread.
        web_server.serve_forever()
    except KeyboardInterrupt:
        # Ctrl+C in the terminal ends up here.
        print("\nStopping the server.")
        web_server.server_close()
