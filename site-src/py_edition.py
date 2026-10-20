"""Python edition: edition values and the annotated builds."""

from pathlib import Path

from diagrams import layers_figure
from lib import box, check, deeper, file_block, goal, make_steps, predict, section, snippet, tryit
from shared_a import concept_database, concept_server, concept_shapes, fill

W = Path(__file__).resolve().parent.parent
PROJECT = W / "vending-py"

E = {
    "slug": "python",
    "shape_label_1": "fetchone() then dict(row)",
    "shape_label_2": "json.dumps(slot)",
    "json_sample": '{"slot_id": "A1", "item_name": "Sparkling Water", "price_cents": 175, "stock": 7}',
    "name": "Python",
    "proj": "vending-py",
    "zip": "downloads/vending-py.zip",
    "server_label": "A Python program",
    "record_word": "Python dictionary",
    "intro_languages": (
        "In this edition the server, the setup script and the database code are written in Python. "
        "The page is plain HTML and CSS plus one short script of about fifty lines. That script is JavaScript, "
        "because a browser can run only JavaScript. It does one job: it asks the server for data and changes the screen to match."
    ),
    "needs": [
        "Python 3.10 or newer. Nothing else needs installing with pip.",
        "A terminal and a code editor.",
        "A browser with developer tools. Chrome, Edge and Firefox all have them.",
    ],
    "http_status_line": "HTTP/1.0 200 OK",
    "http_status_note": (
        "<p>The <dfn>status line</dfn> holds the protocol version, the <dfn>status code</dfn> and a short reason. "
        "Our Python server answers in HTTP/1.0, an older version of the protocol. The code 200 means success.</p>"
    ),
    "http_headers": (
        "Server: BaseHTTP/0.6 Python/3.13.16\n"
        "Date: Sat, 17 Oct 2026 21:33:37 GMT\n"
        "Content-Type: application/json; charset=utf-8\n"
        "Content-Length: 81\n"
        "Cache-Control: no-store"
    ),
    "http_headers_extra": "The Python class added the <code>Server</code> and <code>Date</code> headers without being asked.",
    "json_colon": ": ",
    "json_comma": ", ",
    "contract_note": "So write the contract down, even if only as a table like the one above.",
    "shape2_title": "A Python dictionary in the server",
    "shape2_code": "{'slot_id': 'A1', 'item_name': 'Sparkling Water', 'price_cents': 175, 'stock': 7}",
    "shape_step_1": "<code>fetchone()</code> returns a row, and <code>dict(row)</code> converts it",
    "shape_step_2": "<code>json.dumps(...)</code> serialises the dictionary into text",
    "run_block": (
        "cd vending-py\n"
        "python setup_db.py     # creates the database file (on macOS or Linux you may need to type python3)\n"
        "python server.py       # starts the server and leaves it running"
    ),
    "log_sample": (
        '127.0.0.1 - - [17/Oct/2026 22:33:32] "GET / HTTP/1.1" 200 -\n'
        '127.0.0.1 - - [17/Oct/2026 22:33:32] "GET /style.css HTTP/1.1" 200 -\n'
        '127.0.0.1 - - [17/Oct/2026 22:33:32] "GET /app.js HTTP/1.1" 200 -\n'
        '127.0.0.1 - - [17/Oct/2026 22:33:32] "GET /api/slots HTTP/1.1" 200 -\n'
        '127.0.0.1 - - [17/Oct/2026 22:33:32] "POST /api/slots/A1/buy HTTP/1.1" 200 -'
    ),
    "injection_cmd": "python injection_demo.py",
    "injection_output": (
        "The user typed: A1\n"
        "Joined into the string:\n"
        "  SQL sent to the database: SELECT item_name, stock FROM inventory WHERE slot_id = 'A1'\n"
        "  rows returned: 1\n"
        "Passed as a parameter:\n"
        "  SQL sent to the database: SELECT item_name, stock FROM inventory WHERE slot_id = ? with value 'A1'\n"
        "  rows returned: 1\n"
        "\n"
        "The user typed: x' OR '1'='1\n"
        "Joined into the string:\n"
        "  SQL sent to the database: SELECT item_name, stock FROM inventory WHERE slot_id = 'x' OR '1'='1'\n"
        "  rows returned: 4\n"
        "Passed as a parameter:\n"
        "  SQL sent to the database: SELECT item_name, stock FROM inventory WHERE slot_id = ? with value \"x' OR '1'='1\"\n"
        "  rows returned: 0"
    ),
    "rebuild_note": "",
    "cors_snippet": (
        '<code>self.send_header("Access-Control-Allow-Origin", "http://127.0.0.1:9000")</code> '
        "inside <code>send_body</code>, next to the other headers."
    ),
    "choice_server_title": "The Python standard library for the server, not a framework",
    "choice_server_why": "Every mechanism stays visible: reading the request, routing and writing the response. Nothing needs installing.",
    "choice_server_when": "In real projects, because a framework such as FastAPI or Flask supplies routing, validation, safe static files and a production server. The next section shows the same API in FastAPI.",
    "choice_conn_title": "A new database connection for each request",
    "choice_conn_why": "The server handles each request in its own thread, and a SQLite connection belongs to the thread that made it. Opening a SQLite connection is very cheap.",
    "choice_conn_when": "With a client-server database, opening a connection is slow, so servers keep a pool of connections and lend them out.",
    "body_hint": (
        'To read a body you can use <code>int(self.headers["Content-Length"])</code> to learn how many bytes to read, '
        "then <code>self.rfile.read(n)</code> to read them, and <code>json.loads</code> to parse them."
    ),
    "extra_extension": "",
    "sql_extra": "Python 3.12 and newer also offers <code>python -m sqlite3 vending.db</code>.",
    "static_server": "<code>python -m http.server 9000 --directory public --bind 127.0.0.1</code> (or <code>npx http-server public -p 9000</code> if you prefer Node)",
    "handler_call": 'handle_buy_slot("A1")',
    "route_row_flight": 'ROUTES entry:\n  ("POST", r"/api/slots/([^/]+)/buy", handle_buy_slot)\nhandle_buy_slot("A1")',
    "validate_flight": 'validate_slot_id("a1") returns "A1"',
    "layer_names": {
        "http": "VendingRequestHandler, answer_request, send_json",
        "route": "ROUTES, handle_buy_slot, validate_slot_id",
        "data": "get_all_slots, get_slot, buy_slot",
    },
}

# ------------------------------------------------------------ chunk texts

SETUP_CHUNKS = [
    ("", [], (
        "<p>The top of the file says what it is for and imports three tools.</p>"
        "<ul>"
        "<li><code>sqlite3</code> is Python's built-in <dfn>driver</dfn> for SQLite, a library that knows how to talk to one kind of database.</li>"
        "<li><code>closing</code> makes sure a connection is closed when we finish with it.</li>"
        "<li><code>Path</code> builds file locations that work on any operating system.</li>"
        "</ul>"
        "<p>The database is one file, <code>vending.db</code>. The path starts from <code>__file__</code>, the location of this script, so the file lands beside the script wherever you run it from.</p>"
    )),
    ("# The schema describes", [7], (
        "<p>This text is the <dfn>schema</dfn>, written in SQL.</p>"
        "<ul>"
        "<li><code>DROP TABLE IF EXISTS</code> deletes any old table, so running the script again resets the machine. That is handy in a classroom and dangerous anywhere else.</li>"
        "<li><code>slot_id</code> is the primary key. The database refuses a second row with the same value and builds an index so that lookups by slot are fast.</li>"
        "<li>The two <code>CHECK</code> lines are constraints. The database enforces them even when our code has a bug.</li>"
        "<li>Money is stored as whole cents.</li>"
        "</ul>"
    )),
    ("# Each tuple is one row", [], (
        "<p>A list of <dfn>tuples</dfn>, which are fixed groups of values, one tuple per row. They follow the column order of the <code>INSERT</code> statement below. "
        "The Oat Biscuits start with zero stock on purpose, so that you can see a sold-out slot without buying everything first.</p>"
    )),
    ("# closing() makes sure", [6, 7], (
        "<ul>"
        "<li>We open a <dfn>connection</dfn>. For SQLite this opens the file, and creates it if it does not exist yet.</li>"
        "<li>The inner <code>with connection:</code> is a transaction. Python commits when the block ends normally and rolls back if an exception occurs, so either all four rows are stored or none is.</li>"
        "<li><code>executescript</code> commits whatever came before it, so creating the table is a separate step and the transaction protects only the four inserts.</li>"
        "<li>The question marks are <dfn>placeholders</dfn>. The SQL text and the values reach the database separately, and the experiments after Step 6 show why that matters.</li>"
        "</ul>"
    )),
    ("    # Read the rows back", [6], (
        "<p>Finally we read the rows back, so that you can see what was stored. <code>connection.execute</code> returns a cursor that we can loop over, and each row arrives as a tuple.</p>"
    )),
]

SERVER_CHUNKS = [
    ("", [3], (
        "<p>The imports use only the standard library, so nothing needs installing.</p>"
        "<ul>"
        "<li><code>http.server</code> supplies the pieces of a web server.</li>"
        "<li><code>urlsplit</code> takes a URL apart, <code>re</code> handles text patterns, and <code>json</code> converts between text and data.</li>"
        "<li>Names in capitals are constants, a convention for values that never change while the program runs.</li>"
        "<li><code>HOST</code> decides who may connect. <code>127.0.0.1</code> allows only your own computer, which is the safe choice while you develop.</li>"
        "<li><code>PORT</code> decides which program receives the request.</li>"
        "<li><code>STATIC_FILES</code> lists the only files the server will send. If it sent whatever file the URL named, a visitor could ask for <code>/../server.py</code> and download our code and our database. That attack is <dfn>path traversal</dfn>.</li>"
        "<li><code>SLOT_ID_PATTERN</code> is a <dfn>regular expression</dfn>, a compact pattern for text. This one means one capital letter followed by one digit.</li>"
        "</ul>"
    )),
    ("# --- Errors", [], (
        "<p>The program expects three kinds of trouble, and each gets its own exception class. The classes have no body, because only their names matter.</p>"
        "<p>The data layer never mentions HTTP. When something goes wrong it raises an exception named in the vocabulary of the vending machine, and one place near the end of the file turns those names into status codes. "
        "So we could reuse the data functions in a program that has no web server at all.</p>"
    )),
    ("# --- Data layer", [6], (
        "<p><code>open_connection</code> opens a new connection to the database file. Every request opens its own.</p>"
        "<ul>"
        "<li><code>ThreadingHTTPServer</code> handles each request in a separate thread.</li>"
        "<li>By default a SQLite connection may be used only by the thread that made it.</li>"
        "<li>Opening one costs very little, so a fresh connection per request is safe and simple.</li>"
        "</ul>"
        "<p>A server for PostgreSQL would keep a <dfn>pool</dfn> of ready connections instead, because opening those is slow.</p>"
    )),
    ("def find_slot", [6], (
        "<p>Three functions read data.</p>"
        "<ul>"
        "<li><code>find_slot</code> runs a <dfn>parameterised query</dfn>. The <code>?</code> marks where a value goes, and the tuple supplies it separately.</li>"
        "<li><code>fetchone</code> returns one row, or <code>None</code> when nothing matched. <code>dict(row)</code> turns the row into a dictionary, which is the second shape from Step 5.</li>"
        "<li><code>get_all_slots</code> and <code>get_slot</code> each open a connection, read and close it. <code>with closing(...)</code> guarantees the close, whatever happens inside.</li>"
        "<li><code>get_slot</code> raises <code>NoSuchSlot</code> when <code>find_slot</code> finds nothing.</li>"
        "</ul>"
    )),
    ("def buy_slot", [6, 7], (
        "<p>This is the most important function in the file.</p>"
        "<ul>"
        "<li>We could read the stock, test it in Python and write the new value. That leaves a gap in which two buyers could both see a stock of 1 and both take the last item.</li>"
        "<li>One <code>UPDATE</code> statement leaves no gap, because the database runs it as a single indivisible step. The section on design choices compares the two plans in a diagram.</li>"
        "<li><code>update_result.rowcount</code> says how many rows changed. Zero means the slot does not exist or its stock was already zero, and <code>slot</code> tells us which.</li>"
        "<li>We read the slot inside the same transaction, so the stock we report matches the change we made.</li>"
        "<li>After the transaction closes we decide what happened: no row means <code>NoSuchSlot</code>, zero changes means <code>SoldOut</code>, anything else is a purchase.</li>"
        "</ul>"
    )),
    ("# --- Route layer", [5], (
        "<p>Everything that comes from the URL is untrusted text. <code>validate_slot_id</code> tidies it, checks that the whole text has the expected shape, and raises <code>BadRequest</code> if not.</p>"
        "<p>The queries are already safe from injection because they use parameters. This check is a second layer that gives a clear error early and keeps odd text out of our logs.</p>"
    )),
    ("def handle_list_slots", [4], (
        "<p>The three handlers are thin. Each connects a URL to a data function and validates the input on the way.</p>"
        "<p><code>ROUTES</code> is the API written as a table.</p>"
        "<ul>"
        "<li>In a pattern, <code>([^/]+)</code> means one or more characters that are not a slash.</li>"
        "<li>The parentheses capture them, so the text between the slashes becomes an argument to the handler.</li>"
        "<li>Every web framework builds a table like this for you. The design choices section shows what that looks like.</li>"
        "</ul>"
    )),
    ("# --- HTTP layer", [4], (
        "<p><code>BaseHTTPRequestHandler</code> is a standard library class that reads the raw request for us. It calls the method whose name matches the HTTP method, so a GET calls <code>do_GET</code>. "
        "We send both methods to one method of our own, <code>answer_request</code>, and pass the method's name along.</p>"
    )),
    ("    def answer_request", [4, 8, 9], (
        "<ul>"
        "<li>First the method checks whether the visitor asked for one of our three files.</li>"
        "<li>If not, it walks through <code>ROUTES</code>. <code>fullmatch</code> requires the pattern to match the whole path.</li>"
        "<li><code>handler(*path_match.groups())</code> spreads the captured text into arguments, and whatever the handler returns goes out as JSON with status 200.</li>"
        "<li>The <code>except</code> lines are the one place where exceptions become status codes: 400, 404 and 409.</li>"
        "<li>Any other exception is our own bug. We print it for the developer and send a vague 500 to the client, because Python's error details help attackers more than visitors.</li>"
        "</ul>"
    )),
    ("    def send_static_file", [9], (
        "<p><code>send_json</code> turns the data into text with <code>json.dumps</code> and encodes the text as bytes. "
        "<code>send_body</code> writes the response in the order HTTP demands: the status line, the headers, a blank line and the body.</p>"
        "<p>The class defaults to HTTP/1.0, which closes the connection after each response. That is slower than modern practice and fine for learning.</p>"
    )),
    ("# This block runs only", [3], (
        "<ul>"
        "<li><code>ThreadingHTTPServer((HOST, PORT), VendingRequestHandler)</code> asks the operating system to listen on that address. It creates a <code>VendingRequestHandler</code> for each request, in a new thread each time.</li>"
        "<li><code>serve_forever</code> loops and waits.</li>"
        "<li><code>if __name__ == \"__main__\"</code> means the block runs only when you start this file directly. The optional FastAPI file imports our data functions without starting a second server.</li>"
        "</ul>"
    )),
]

INDEX_CHUNKS = [
    ("", [], (
        "<ul>"
        "<li>The first line tells the browser this is an HTML5 document.</li>"
        "<li><code>charset=\"utf-8\"</code> says how to turn bytes into characters, and the <code>viewport</code> line makes the page fit a phone screen.</li>"
        "<li>The title appears on the browser tab, and <code>link</code> loads the stylesheet.</li>"
        "<li><code>/style.css</code> begins with a slash, so the browser asks the server that delivered this page. That request goes through the same stations as an API request.</li>"
        "</ul>"
    )),
    ("<body>", [11], (
        "<p>The browser reads this file and builds the <dfn>DOM</dfn>, a tree with one object per element. What you see is a drawing of that tree, and the script will change the tree later.</p>"
        "<ul>"
        "<li>The <code>id</code> attributes are names the script uses to find elements.</li>"
        "<li><code>#slots</code> starts empty. The script fills it with one card per row in the database.</li>"
        "</ul>"
    )),
    ("  <!-- A template", [11], (
        "<p>A <code>&lt;template&gt;</code> holds HTML that the browser reads but neither shows nor runs. The script copies it once per slot and fills in the copy.</p>"
        "<ul>"
        "<li>HTML is the clearest way to describe structure.</li>"
        "<li>Pieces of HTML joined together inside script strings are hard to read and easy to get wrong.</li>"
        "<li>Each element has a class so that the script and the stylesheet can refer to it.</li>"
        "</ul>"
    )),
    ("  <!-- The script comes last", [], (
        "<p>The script comes last, so every element it looks for already exists when it runs. <code>type=\"module\"</code> opts in to the modern script mode, in which the names inside the file stay private to the file.</p>"
    )),
]

CSS_CHUNKS = [
    ("", [], (
        "<p>The <code>:root</code> block defines <dfn>custom properties</dfn>, named values such as <code>--accent</code> that the rest of the stylesheet reads with <code>var(--accent)</code>. Changing a colour means editing one line.</p>"
        "<p>The body is a <code>flex</code> container, which here centres the machine horizontally.</p>"
    )),
    ("/* min() means", [], (
        "<p><code>width: min(100%, 480px)</code> means as wide as 480 pixels but never wider than the screen, so the machine fits on a phone.</p>"
    )),
    ("/* A grid with two", [], (
        "<p>The slots form a grid of two equal columns, and each card is a slightly lighter box. Nothing here depends on the data, so the same styles work for one slot or twenty.</p>"
    )),
    ("/* The script only adds", [11, 12], (
        "<p>The script never sets colours. When a slot has no stock, it adds the class <code>sold-out</code> and sets the button's <code>disabled</code> property. This stylesheet decides what those states look like.</p>"
        "<p>The script says what state the card is in, and the stylesheet says how that state looks. A designer can change the appearance without touching the logic.</p>"
    )),
]

JS_CHUNKS = [
    ("", [11], (
        "<ul>"
        "<li>The first three constants look up elements by <code>id</code> and keep them in variables, so we search the page once and not on every click.</li>"
        "<li><code>Intl.NumberFormat</code> is a formatter the browser provides. With the locale <code>en-IE</code> and the currency <code>EUR</code> it writes 1.75 as <code>€1.75</code>.</li>"
        "<li>Writing <code>\"€\" + (cents / 100).toFixed(2)</code> works until you meet a place with different conventions, so we let the formatter decide.</li>"
        "</ul>"
    )),
    ("// Send a request to our API", [2, 10], (
        "<p>This function wraps every API call, so the rest of the script never repeats the checks.</p>"
        "<ul>"
        "<li>Inside an <code>async</code> function, <code>await</code> pauses that function, and only that one, until a promise settles. The browser stays responsive meanwhile.</li>"
        "<li><code>fetch</code> sends the request at Station 2, and its reply arrives at Station 10.</li>"
        "<li>If no response arrives at all, <code>fetch</code> rejects, and we turn that into a friendlier message.</li>"
        "<li>If a response arrives with a bad status such as 404 or 409, <code>fetch</code> still counts it as success, so we check <code>response.ok</code> ourselves and pass on the server's own message.</li>"
        "<li><code>response.json()</code> returns a promise too, so it needs its own <code>await</code>.</li>"
        "</ul>"
    )),
    ("// Build one card for one slot", [11], (
        "<p>This function turns one slot (the fourth shape from Step 5) into one card (the fifth). <code>cloneNode(true)</code> makes a deep copy of the template, so the template stays unchanged for the next card.</p>"
        "<ul>"
        "<li>Every line that shows data uses <code>textContent</code>, which treats the value as plain text.</li>"
        "<li>With <code>innerHTML</code>, an item name containing a script tag would run. That attack is cross-site scripting.</li>"
        "<li>The function returns a card that is not on the screen yet, because nothing has attached it to the page.</li>"
        "</ul>"
    )),
    ("// Ask the server for every slot", [10, 11, 12], (
        "<ul>"
        "<li><code>slots.map(createSlotCard)</code> converts an array of data into an array of cards.</li>"
        "<li><code>replaceChildren(...)</code> swaps the contents of <code>#slots</code> for them in one step. That is the moment the DOM changes, and the browser repaints at Station 12.</li>"
        "<li><code>try</code> and <code>catch</code> show any error in the status line, so the visitor sees what went wrong.</li>"
        "</ul>"
    )),
    ("// One listener on the whole list", [1, 2, 10, 11], (
        "<p>We attach one listener to the container and not one to each button, because the buttons do not exist yet when this line runs. A click on a button <dfn>bubbles</dfn> up through its parents, so the container hears it. This is <dfn>event delegation</dfn>.</p>"
        "<ul>"
        "<li>This function is Station 1.</li>"
        "<li>It reads the slot id from <code>slotCard.dataset.slot</code>, sends a <code>POST</code>, and swaps in a new card built from the server's reply.</li>"
        "<li>We draw what the server said and not what we guess, so if someone bought the last item a moment earlier, the card tells the truth.</li>"
        "</ul>"
    )),
    ("// Show the slots as soon", [2], (
        "<p>The last line runs once when the script loads and sends the first request.</p>"
    )),
]

FASTAPI_CHUNKS = [
    ("", [], (
        "<p>This file reuses our own data layer with <code>from server import ...</code>. Importing <code>server.py</code> does not start the server, because of the <code>__main__</code> guard. "
        "FastAPI is a third-party framework, so you install it with pip.</p>"
    )),
    ("app = FastAPI", [], (
        "<p><code>FastAPI(...)</code> creates the application. <code>SlotId</code> is a type that says a slot id must match a pattern, and the framework checks it for us. It replaces our <code>validate_slot_id</code>.</p>"
    )),
    ("# Each decorator adds", [4], (
        "<p>The decorators <code>@app.get(...)</code> and <code>@app.post(...)</code> add rows to a route table that the framework keeps. These are the same three rows as our <code>ROUTES</code>, and each function shrinks to one line.</p>"
        "<p>The framework converts the returned dictionary to JSON, sets the headers, and turns the <code>{slot_id}</code> part of the path into an argument.</p>"
    )),
    ("# These handlers turn exceptions", [8, 9], (
        "<p>The exception handlers do the job of our <code>except</code> lines. We keep the same <code>{\"error\": ...}</code> shape so the page does not change.</p>"
        "<p>Without them the framework answers with <code>{\"detail\": ...}</code> and status 422 for a malformed id. Frameworks come with defaults, and keeping your API's contract is still your job.</p>"
    )),
    ("# Serve the page files", [], (
        "<p>The last line serves the <code>public</code> folder. It must come last, because the routes above are checked first.</p>"
    )),
]

# ------------------------------------------------------------- sections


def fw_html():
    intro = (
        '<div class="prose"><h3>Where frameworks fit</h3>'
        "<ul>"
        "<li>Real projects rarely write server plumbing by hand. A <dfn>framework</dfn> provides routing, validation, safe static files, error handling and a production server.</li>"
        "<li>We wrote the plumbing ourselves so that each mechanism is visible once.</li>"
        "<li>Below is the same API in FastAPI, a popular Python framework. It is optional, and it is in the download as <code>server_fastapi.py</code>.</li>"
        "</ul></div>"
    )
    block = file_block(PROJECT, "server_fastapi.py", FASTAPI_CHUNKS, "python", "in vending-py/ (optional)")
    outro = (
        '<div class="prose"><ul>'
        "<li>Run it with <code>pip install fastapi uvicorn</code> and then <code>uvicorn server_fastapi:app --port 8000</code>.</li>"
        "<li>FastAPI writes documentation for your API automatically. Visit <code>http://127.0.0.1:8000/docs</code> to see the endpoints from Step 3 in a standard format called OpenAPI.</li>"
        "</ul></div>"
    )
    return intro + block + outro


E["frameworks_html"] = fw_html()


def sec_build_db():
    body = goal(
        [
            "Create the vending machine's database as a file.",
            "Run a script that fills it with four slots.",
            "See the stored rows printed back.",
        ]
    )
    body += concept_database(E)
    body += make_steps(
        [
            "Create a folder called <code>vending-py</code> and open a terminal in it.",
            "Create a file called <code>setup_db.py</code> and type or paste the code below.",
            "Run <code>python setup_db.py</code> (on macOS or Linux you may need <code>python3</code>).",
        ]
    )
    body += file_block(PROJECT, "setup_db.py", SETUP_CHUNKS, "python", "in vending-py/")
    body += check(
        [
            "The terminal prints the four rows below.",
            "A new file called <code>vending.db</code> sits beside the script. That file is the whole database.",
            "Run the script a second time and you get the same four rows. Which line made that safe?",
        ]
    )
    body += snippet(
        "('A1', 'Sparkling Water', 175, 8)\n('A2', 'Salted Peanuts', 125, 5)\n('B1', 'Chocolate Bar', 200, 3)\n('B2', 'Oat Biscuits', 150, 0)",
        "text",
        "Expected output",
        copy=False,
    )
    body += box(
        "note",
        "Why we start here",
        "<p>The database comes first, with no web code at all. If something goes wrong later, you already know the database part works.</p>",
    )
    return section("build-db", "Step 2", "Build the database", body)


def sec_build_server():
    body = goal(
        [
            "Write the server in one file, in three layers.",
            "Offer an API with three routes: list the slots, show one slot, buy from a slot.",
            "Open the API in a browser and see JSON, with no page involved.",
        ]
    )
    body += concept_server(E)
    body += (
        '<div class="prose"><h3>Build it in three layers</h3>'
        "<ul>"
        "<li>The <strong>data layer</strong> talks to the database and knows nothing about HTTP.</li>"
        "<li>The <strong>route layer</strong> connects URLs to data functions and checks input.</li>"
        "<li>The <strong>HTTP layer</strong> reads requests and writes responses, and the last lines start the server.</li>"
        "<li>Each layer uses only the one beneath it, so you can change one without disturbing the others. The file lists the layers in this order.</li>"
        "</ul></div>"
    )
    body += layers_figure(E["layer_names"], E["slug"])
    body += make_steps(
        [
            "In <code>vending-py</code>, create a file called <code>server.py</code> and type or paste the code below.",
            "Run <code>python server.py</code>. It stays running, and that is correct.",
            "Visit <code>http://127.0.0.1:8000/api/slots</code> in a browser.",
        ]
    )
    body += file_block(PROJECT, "server.py", SERVER_CHUNKS, "python", "in vending-py/")
    body += check(
        [
            "The browser shows a line of JSON with four slots. You have used the API with no page and no script.",
            "The terminal printed one log line for your request.",
            "<code>http://127.0.0.1:8000/api/slots/A1</code> shows one slot, and <code>http://127.0.0.1:8000/api/slots/hello</code> shows an error message.",
        ]
    )
    return section("build-server", "Step 3", "Build the server and its API", body)


def sec_build_page():
    body = goal(
        [
            "Write the page's structure in HTML.",
            "Write its appearance in CSS.",
            "See the page load, still without any slots.",
        ]
    )
    body += (
        '<div class="prose"><h3>One idea first: the DOM</h3>'
        "<ul>"
        "<li>When a browser loads an HTML file it builds the <dfn>DOM</dfn> (Document Object Model), a tree with one object per element.</li>"
        "<li>The screen shows a drawing of that tree.</li>"
        "<li>A script can change the tree, and that is how a server's answer reaches the screen.</li>"
        "<li>The page itself has no logic. The HTML says what exists and the CSS says how it looks.</li>"
        "</ul></div>"
    )
    body += make_steps(
        [
            "In <code>vending-py</code>, create a folder called <code>public</code>.",
            "In it, create <code>index.html</code> and <code>style.css</code> with the code below.",
            "With the server still running, open <code>http://127.0.0.1:8000</code>.",
        ]
    )
    body += file_block(PROJECT, "public/index.html", INDEX_CHUNKS, "html", "in vending-py/public/")
    body += file_block(PROJECT, "public/style.css", CSS_CHUNKS, "css", "in vending-py/public/")
    body += check(
        [
            "You see the machine's heading and the text <em>Loading...</em>.",
            "No slots appear yet, because nothing asks the server for them. That is Step 5.",
            "The terminal prints an error about <code>app.js</code>, because that file does not exist yet. This is expected.",
        ]
    )
    return section("build-page", "Step 4", "Build the page", body)


def sec_build_script():
    body = goal(
        [
            "Write the script that asks the server for the slots.",
            "Draw one card per slot from the server's reply.",
            "Make the Buy button work, so the whole journey from Step 1 happens.",
        ]
    )
    body += (
        '<div class="prose"><p>The script has one job: ask the server for data and change the page to match the reply. '
        "A browser can run only JavaScript, so this part is JavaScript, and it stays short on purpose. Everything with rules in it, such as the stock count and the validation, lives in the Python server.</p></div>"
    )
    body += concept_shapes(E)
    body += make_steps(
        [
            "In <code>vending-py/public</code>, create <code>app.js</code> and type or paste the code below.",
            "Reload <code>http://127.0.0.1:8000</code>.",
        ]
    )
    body += file_block(PROJECT, "public/app.js", JS_CHUNKS, "javascript", "in vending-py/public/")
    body += check(
        [
            "Four cards appear: Sparkling Water, Salted Peanuts, Chocolate Bar and Oat Biscuits.",
            "Oat Biscuits is greyed out, because its stock is zero.",
            "Press Buy on Chocolate Bar three times. The count falls to 0 and the button is disabled.",
            "Reload the page. The count stays at 0, because it lives in the database.",
        ]
    )
    body += predict(
        "<p>Suppose the reply took five seconds. What would the visitor see in that time, and how could we improve it? Think about it, then watch the Network tab in Step 6.</p>"
    )
    return section("build-script", "Step 5", "Build the script", body)


# ------------------------------------------------------- the browser demo

ADAPTER_CHUNKS = [
    ("", [], (
        "<p>This file is all of the new code. A browser cannot open a network port, so the bottom layer of our server, the one that reads from sockets, has no place to run. "
        "The two layers above it never needed sockets, so they run unchanged, and we write only a replacement for the top.</p>"
        "<p><code>import server</code> loads the real <code>server.py</code>. Because of the <code>__main__</code> guard, importing it does not start a server.</p>"
    )),
    ("def answer", [4, 5, 8], (
        "<p>The function takes the method and path as the browser sent them and returns a status code and body text.</p>"
        "<ul>"
        "<li>The loop is the one from the real <code>answer_request</code>. It walks the real <code>ROUTES</code> table, and the first matching row calls the real handler.</li>"
        "<li>The data layer then runs real SQL on a real SQLite database, which here lives in the page's memory.</li>"
        "</ul>"
    )),
    ("    # The same translation", [9], (
        "<p>These lines repeat the translation from exceptions to status codes, because it belonged to the HTTP layer we replaced. A request for <code>B2</code>, which has no stock, ends here as a 409 with the same message the real server sends.</p>"
    )),
]


def sec_try_first():
    body = (
        goal(
            [
                "Press the buttons on the finished machine before you build anything.",
                "Know what is real in this demo and what is simulated.",
            ],
            "In this section you will",
        )
        + '<figure class="demo"><iframe src="demo/vending.html" title="The vending machine page, answered by Python running in the browser" height="560" loading="lazy"></iframe>'
        "<figcaption>The vending machine. The page is the real one from the project, and a simulated server answers its requests. "
        "If nothing appears, open <a href=\"demo/vending.html\">the machine on its own page</a>.</figcaption></figure>"
        + tryit(
            "<p>Open the developer tools, choose the <strong>Network</strong> tab, reload the machine's own page, and press Buy. "
            "The <code>/api/slots</code> rows show that a service worker answered, and the response headers include <code>X-Served-By</code>.</p>"
        )
        + deeper(
            "What is real here, and what is simulated",
            "<p>A web page cannot open a network port, so no real server program is running. Three real things are running.</p>"
            "<ul>"
            "<li><dfn>Pyodide</dfn> is the Python interpreter compiled for browsers. It runs the real <code>setup_db.py</code> and the real data layer and route table from <code>server.py</code>, including real SQL on a real SQLite database.</li>"
            "<li>The page's own script, <code>app.js</code>, is the file you will write in Step 5, with no changes.</li>"
            "<li>A <dfn>service worker</dfn>, a script that sits between a page and the network, catches each request whose address starts with <code>/api/</code> and hands it to Python.</li>"
            "</ul>"
            "<p>The simulated part is the wire. No bytes travel between two programs, so Stations 3 and 9 are imitated, and the HTTP layer of the server is replaced by the short file below. That replacement is possible because the layers were kept apart.</p>"
            + file_block(W / "demo-src", "py/adapter.py", ADAPTER_CHUNKS, "python", "the replacement for the HTTP layer")
            + "<p>The real server's headers include <code>Server</code> and <code>Date</code>. This reply has neither, because no real server wrote it.</p>",
        )
        + '<div class="prose"><ul>'
        '<li>Want to change the pages, the SQL or the server and watch each request travel? The <a href="workbench/index.html">workbench</a> shows the browser, the server and the database side by side, with a timeline.</li>'
        "<li>When you are ready, start with Step 1. In Step 6 you run a real server on your own computer.</li>"
        "</ul></div>"
    )
    return section("try-first", "Try it first", "The finished machine, running in your browser", body)
