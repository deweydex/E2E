"""Python edition: edition values and the annotated builds."""

from pathlib import Path

from diagrams import layers_figure
from lib import box, file_block, predict, section, snippet, tryit
from shared_a import fill

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
        "In this edition the server, the setup script and the database code are all written in Python. "
        "The page uses plain HTML and CSS plus one short script of about fifty lines of code. That script is JavaScript, "
        "because a browser can run only JavaScript, and it does one job: it asks the server for data and changes the screen to match."
    ),
    "prereq": (
        "You need Python 3.10 or newer, a terminal, a code editor, and a browser with developer tools. Chrome, Edge and Firefox all have them. "
        "Nothing needs to be installed with pip."
    ),
    "http_status_line": "HTTP/1.0 200 OK",
    "http_status_note": (
        "<p>The first line of a response is the <dfn>status line</dfn>. It holds the protocol version, the <dfn>status code</dfn> and a short reason. "
        "Our Python server answers in HTTP/1.0, an older version of the protocol, and the code 200 means success.</p>"
    ),
    "http_headers": (
        "Server: BaseHTTP/0.6 Python/3.13.16\n"
        "Date: Sat, 17 Oct 2026 21:33:37 GMT\n"
        "Content-Type: application/json; charset=utf-8\n"
        "Content-Length: 81\n"
        "Cache-Control: no-store"
    ),
    "http_headers_extra": "The <code>Server</code> and <code>Date</code> headers were added by the Python class without being asked.",
    "json_colon": ": ",
    "json_comma": ", ",
    "contract_note": "That is why the contract is worth writing down, even if only as a table like the one above.",
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
        "<p>The first lines say what the file is for and bring in three tools. <code>sqlite3</code> is Python's built-in <dfn>driver</dfn> for SQLite, which means a library that knows how to talk to one kind of database. "
        "<code>closing</code> makes sure that a connection is closed when we finish with it, and <code>Path</code> builds file locations that work on any operating system.</p>"
        "<p>The database is a single file called <code>vending.db</code>. Because the path starts from <code>__file__</code>, the location of this script, the file lands beside the script wherever you run it from.</p>"
    )),
    ("# The schema describes", [7], (
        "<p>This text is the <dfn>schema</dfn>, written in SQL. <code>DROP TABLE IF EXISTS</code> deletes any old table, so running the script again resets the machine. "
        "That is convenient in a classroom and dangerous anywhere else, so the line deserves a pause.</p>"
        "<p><code>slot_id</code> is the <dfn>primary key</dfn>. The database refuses a second row with the same value, and it builds an index on the column so that lookups by slot are fast. "
        "The two <code>CHECK</code> lines are <dfn>constraints</dfn>, rules that the database enforces even when our own code has a bug. Money is stored as whole cents, for the reason given in Part 2.</p>"
    )),
    ("# Each tuple is one row", [], (
        "<p>A list of <dfn>tuples</dfn>, which are fixed groups of values, with one tuple for each row. They follow the column order that the <code>INSERT</code> statement names below. "
        "The Oat Biscuits start with zero stock on purpose, so that you can see a sold-out slot without buying everything first.</p>"
    )),
    ("# closing() makes sure", [6, 7], (
        "<p>We open a <dfn>connection</dfn>. For SQLite this opens the file, and it creates the file if it does not exist yet.</p>"
        "<p>The inner <code>with connection:</code> is a <dfn>transaction</dfn>. Python commits the changes when the block ends normally, and it rolls them back if an exception occurs. "
        "One detail deserves care: <code>executescript</code> commits whatever came before it, so creating the table is its own step, and the transaction protects the four inserts. Either all four rows are stored or none of them is.</p>"
        "<p>The question marks are <dfn>placeholders</dfn>. The SQL text and the values reach the database separately, and Experiment 3 in Part 12 shows why that matters.</p>"
    )),
    ("    # Read the rows back", [6], (
        "<p>Finally we read the rows back so that you can see what was stored. <code>connection.execute</code> returns a cursor, an object that we can loop over, and each row arrives as a tuple.</p>"
    )),
]

SERVER_CHUNKS = [
    ("", [3], (
        "<p>The imports bring in only the standard library, so nothing needs installing. <code>http.server</code> supplies the pieces of a web server, <code>urlsplit</code> takes a URL apart, "
        "<code>re</code> handles text patterns, and <code>json</code> converts between text and data.</p>"
        "<p>Names in capitals are constants, a convention for values that never change while the program runs. <code>HOST</code> decides who may connect, and <code>127.0.0.1</code> allows only your own computer, "
        "which is the safe choice while you develop. <code>PORT</code> decides which program receives the request.</p>"
        "<p><code>STATIC_FILES</code> is a dictionary of the only files that the server will send. If it sent whatever file the URL named, a visitor could request a path such as <code>/../server.py</code> and download our code and our database. "
        "That attack is called <dfn>path traversal</dfn>, and a fixed list prevents it. <code>SLOT_ID_PATTERN</code> is a <dfn>regular expression</dfn>, a compact pattern for text. This one means one capital letter followed by one digit.</p>"
    )),
    ("# --- Errors", [], (
        "<p>The program expects three kinds of trouble, and each one gets its own exception class. The classes have no body of their own, because only their names matter.</p>"
        "<p>The data layer below never mentions HTTP. When something goes wrong it raises an exception named in the vocabulary of the vending machine, and one place near the end of the file translates those names into status codes. "
        "That separation means we could reuse the data functions in a program that has no web server at all.</p>"
    )),
    ("# --- Data layer", [6], (
        "<p><code>open_connection</code> opens a new connection to the database file. Every request will open its own, because <code>ThreadingHTTPServer</code> handles each request in a separate thread, "
        "and by default a SQLite connection may be used only by the thread that created it. Opening a SQLite connection costs very little, so a fresh one per request is both safe and simple.</p>"
        "<p>A server for a client-server database such as PostgreSQL would keep a <dfn>pool</dfn> of ready connections instead, because opening those is slow.</p>"
    )),
    ("def find_slot", [6], (
        "<p>Three functions read data. <code>find_slot</code> runs a <dfn>parameterised query</dfn>, in which the <code>?</code> marks where a value goes and the tuple supplies it separately. "
        "<code>fetchone</code> returns one row, or <code>None</code> when nothing matched, and <code>dict(row)</code> turns a row into a dictionary, which is shape 2 in Part 6.</p>"
        "<p><code>get_all_slots</code> and <code>get_slot</code> each open a connection, read, and close it again. The <code>with closing(...)</code> form guarantees the close, whatever happens inside the block. "
        "<code>get_slot</code> raises <code>NoSuchSlot</code> when <code>find_slot</code> finds nothing.</p>"
    )),
    ("def buy_slot", [6, 7], (
        "<p>This is the most important function in the file. We could have read the stock, tested it in Python, and then written the new value. That plan leaves a gap, and two buyers who arrive together could both see a stock of 1, both pass the test, and both take the last item. "
        "The single <code>UPDATE</code> statement leaves no gap, because the database runs it as one indivisible step.</p>"
        "<p>The diagram in Part 13 compares the two plans. After the statement, <code>update_result.rowcount</code> says how many rows it changed. Zero means that either the slot does not exist or its stock was already zero, and we find out which by looking at <code>slot</code>.</p>"
        "<p>We read the slot inside the same transaction so that the stock we report matches the change we made. Only after the transaction closes do we decide what happened: no row means <code>NoSuchSlot</code>, zero changes means <code>SoldOut</code>, and anything else is a successful purchase.</p>"
    )),
    ("# --- Route layer", [5], (
        "<p>Everything that comes from the URL is untrusted text. <code>validate_slot_id</code> tidies it and checks that the whole text has the shape we expect, and it raises <code>BadRequest</code> when it does not. "
        "The queries are already safe from injection because they use parameters, so this check is a second layer. It gives a clear error early, and it keeps odd text out of our logs.</p>"
    )),
    ("def handle_list_slots", [4], (
        "<p>The three handlers are deliberately thin. Each one connects a URL to a data function and validates the input on the way.</p>"
        "<p><code>ROUTES</code> is the API written as a table. In the patterns, <code>([^/]+)</code> means one or more characters that are not a slash, and the parentheses capture them, "
        "so the text between the slashes becomes an argument to the handler. Every web framework builds a table like this for you, and Part 13 shows what that looks like.</p>"
    )),
    ("# --- HTTP layer", [4], (
        "<p><code>BaseHTTPRequestHandler</code> is a class from the standard library that reads the raw request for us. It calls the method whose name matches the HTTP method, so a GET request calls <code>do_GET</code>. "
        "We send both methods to one method of our own, <code>answer_request</code>, and pass the method's name along.</p>"
    )),
    ("    def answer_request", [4, 8, 9], (
        "<p>This method first checks whether the visitor asked for one of our three files. If not, it walks through <code>ROUTES</code>, and <code>fullmatch</code> requires the pattern to match the whole path. "
        "The call <code>handler(*path_match.groups())</code> uses the star to spread the captured text into arguments, and whatever the handler returns goes out as JSON with status 200.</p>"
        "<p>All of this sits inside a <code>try</code> block, so the <code>except</code> lines are the one place where exceptions become status codes: 400, 404 and 409 for the three expected problems. "
        "Any other exception is a bug of ours, so we print it for the developer and send a vague 500 to the client. Python's error details help attackers more than they help visitors, so they stay in the terminal.</p>"
    )),
    ("    def send_static_file", [9], (
        "<p><code>send_json</code> serialises the data with <code>json.dumps</code> and then encodes the text as bytes. <code>send_body</code> writes the response in the order that HTTP demands: "
        "the status line, the headers, a blank line, and the body. These are exactly the lines in the captured response in Part 4.</p>"
        "<p>The status line there says HTTP/1.0 because this class defaults to the older version of the protocol, which closes the connection after each response. "
        "That is slower than modern practice and perfectly good for learning.</p>"
    )),
    ("# This block runs only", [3], (
        "<p><code>ThreadingHTTPServer((HOST, PORT), VendingRequestHandler)</code> asks the operating system to listen on that address, and it promises to create a <code>VendingRequestHandler</code> for each incoming request, in a new thread each time. "
        "<code>serve_forever</code> then loops and waits.</p>"
        "<p>The condition <code>if __name__ == \"__main__\"</code> means that this block runs only when you start the file directly. Part 13 relies on that, because there a second file imports our data functions without starting a second server.</p>"
    )),
]

INDEX_CHUNKS = [
    ("", [], (
        "<p>The first line tells the browser that this is an HTML5 document. <code>charset=\"utf-8\"</code> says how to turn bytes into characters, and the <code>viewport</code> line makes the page fit a phone screen. "
        "The title appears on the browser tab, and <code>link</code> loads the stylesheet.</p>"
        "<p>The address <code>/style.css</code> begins with a slash, so the browser asks the server that delivered this page. That request travels through the same stations as an API request, and our server answers it from its list of static files.</p>"
    )),
    ("<body>", [11], (
        "<p>When the browser reads this file it builds the <dfn>DOM</dfn>, a tree with one object for each element. Here <code>main</code> contains the heading, the status paragraph and the section. "
        "What you see on screen is a drawing of that tree, and the script will change the tree later.</p>"
        "<p>The <code>id</code> attributes are names that the script uses to find elements. The element <code>#slots</code> starts empty, because the script fills it with one card for each row in the database.</p>"
    )),
    ("  <!-- A template", [11], (
        "<p>A <code>&lt;template&gt;</code> holds HTML that the browser reads but does not display and does not run. The script copies it once for each slot and fills in the copies. "
        "We keep the structure of the card here, in HTML, because HTML is the clearest way to describe structure, and because pieces of HTML joined together inside script strings are hard to read and easy to get wrong. "
        "Each element has a class so that the script and the stylesheet can refer to it.</p>"
    )),
    ("  <!-- The script comes last", [], (
        "<p>The script comes last, so every element that it looks for already exists when it runs. <code>type=\"module\"</code> opts in to the modern script mode, in which the browser runs the script after it has read the page, and in which the names inside the file stay private to the file.</p>"
    )),
]

CSS_CHUNKS = [
    ("", [], (
        "<p>The <code>:root</code> block defines <dfn>custom properties</dfn>, named values such as <code>--accent</code> that the rest of the stylesheet reads with <code>var(--accent)</code>. Changing a colour then means editing one line. "
        "The body is a <code>flex</code> container, which here centres the machine horizontally.</p>"
    )),
    ("/* min() means", [], (
        "<p>The declaration <code>width: min(100%, 480px)</code> means as wide as 480 pixels, but never wider than the screen, so the machine fits on a phone.</p>"
    )),
    ("/* A grid with two", [], (
        "<p>The slots form a <code>grid</code> with two equal columns, and each card is a slightly lighter box. Nothing here depends on the data, so the same styles work for one slot or for twenty.</p>"
    )),
    ("/* The script only adds", [11, 12], (
        "<p>The script never sets colours. When a slot has no stock, it adds the class <code>sold-out</code> to the card and sets the button's <code>disabled</code> property, and this stylesheet decides what those states look like. "
        "The script says what state the card is in, and the stylesheet says how that state looks. Keeping the two jobs apart means that a designer can change the appearance without touching the logic.</p>"
    )),
]

JS_CHUNKS = [
    ("", [11], (
        "<p>The first three constants look up elements by their <code>id</code> and keep them in variables, so that we search the page once and not on every click.</p>"
        "<p><code>Intl.NumberFormat</code> is a formatter that the browser provides. With the locale <code>en-IE</code> and the currency <code>EUR</code> it writes 1.75 as <code>€1.75</code>. "
        "We could have written <code>\"€\" + (cents / 100).toFixed(2)</code>, and that works until we meet a place whose conventions differ, so we let the formatter decide.</p>"
    )),
    ("// Send a request to our API", [2, 10], (
        "<p>This function wraps every API call, so the rest of the script never repeats the checks. Inside an <code>async</code> function, <code>await</code> pauses that function, and only that one, until a promise settles. "
        "The browser stays responsive meanwhile, which matters because a network reply can take a noticeable time. <code>fetch</code> sends the request at Station 2, and its reply arrives at Station 10.</p>"
        "<p>A call can fail in two different ways. When no response arrives at all, <code>fetch</code> itself rejects, and we turn that into a friendlier message. "
        "When a response arrives with a bad status such as 404 or 409, <code>fetch</code> counts it as success, because a reply did arrive, so we check <code>response.ok</code> ourselves and pass on the server's own message. "
        "<code>response.json()</code> returns a promise as well, so it needs its own <code>await</code>.</p>"
    )),
    ("// Build one card for one slot", [11], (
        "<p>This function turns one slot, which is shape 4 in Part 6, into one card, which is shape 5. <code>cloneNode(true)</code> makes a deep copy of the template, so the template stays unchanged for the next card.</p>"
        "<p>Notice <code>textContent</code> in every line that shows data. It treats the value as plain text. If we used <code>innerHTML</code> and an item name contained a script tag, the browser would run it, and that attack is called cross-site scripting. "
        "The function returns a card that is not on the screen yet, because nothing has attached it to the page.</p>"
    )),
    ("// Ask the server for every slot", [10, 11, 12], (
        "<p><code>slots.map(createSlotCard)</code> converts an array of data into an array of cards, and <code>replaceChildren(...)</code> swaps the contents of <code>#slots</code> for them in one step. "
        "That call is the moment when the DOM changes, and the browser repaints at Station 12. The <code>try</code> and <code>catch</code> show any error message in the status line, so the visitor sees what went wrong.</p>"
    )),
    ("// One listener on the whole list", [1, 2, 10, 11], (
        "<p>We attach one listener to the container and not one to each button, because the buttons do not exist yet when this line runs. A click on a button <dfn>bubbles</dfn> up through its parents, so the container hears it. "
        "This technique is called <dfn>event delegation</dfn>.</p>"
        "<p>This function is Station 1. We read the slot id back from <code>slotCard.dataset.slot</code>, send a <code>POST</code> request, and swap in a new card made from the server's reply. "
        "We draw what the server said and not what we guess, so if another person bought the last item a moment earlier, the card tells the truth.</p>"
    )),
    ("// Show the slots as soon", [2], (
        "<p>The last line runs once when the script loads, and it sends the first request.</p>"
    )),
]

FASTAPI_CHUNKS = [
    ("", [], (
        "<p>This file reuses our own data layer with <code>from server import ...</code>. Importing <code>server.py</code> does not start the server, because of the <code>if __name__ == \"__main__\"</code> guard. "
        "FastAPI is a third-party framework, so you install it with pip.</p>"
    )),
    ("app = FastAPI", [], (
        "<p><code>FastAPI(...)</code> creates the application object. <code>SlotId</code> is a type that says a slot id must match a pattern, and the framework checks it for us. It replaces our <code>validate_slot_id</code> function.</p>"
    )),
    ("# Each decorator adds", [4], (
        "<p>The decorators <code>@app.get(...)</code> and <code>@app.post(...)</code> add rows to a route table that the framework keeps. These are the same three rows as our <code>ROUTES</code> list, and each function shrinks to one line. "
        "The framework converts the returned dictionary to JSON and sets the headers. It also turns the <code>{slot_id}</code> part of the path into an argument.</p>"
    )),
    ("# These handlers turn exceptions", [8, 9], (
        "<p>The exception handlers do the job of our <code>except</code> lines. We keep the same <code>{\"error\": ...}</code> shape so that the page does not need to change. "
        "Without them the framework would answer with its own shape, <code>{\"detail\": ...}</code>, and with status 422 for a malformed id. Frameworks come with defaults, and the contract of your API remains yours to keep.</p>"
    )),
    ("# Serve the page files", [], (
        "<p>The last line serves the <code>public</code> folder. It must come last, because the routes above are checked first.</p>"
    )),
]

# ------------------------------------------------------------- sections


def fw_html():
    intro = (
        '<div class="prose"><h3>Where frameworks fit</h3>'
        "<p>In a real project you would rarely write the plumbing of a server by hand. A <dfn>framework</dfn> provides routing, input validation, safe static file serving, error handling and a production-ready server, "
        "and it lets you write only the parts that are particular to your application. We built the plumbing ourselves so that each mechanism is visible once. To see the difference, here is the same API in FastAPI, a popular Python framework. "
        "It is optional, and it is included in the download as <code>server_fastapi.py</code>.</p></div>"
    )
    block = file_block(PROJECT, "server_fastapi.py", FASTAPI_CHUNKS, "python", "in vending-py/ (optional)")
    outro = (
        '<div class="prose"><p>You run it with <code>pip install fastapi uvicorn</code> and then <code>uvicorn server_fastapi:app --port 8000</code>. '
        "FastAPI also writes documentation for your API automatically. Visit <code>http://127.0.0.1:8000/docs</code> and you find the endpoints that we described by hand in Part 5, laid out in a standard format called OpenAPI that other tools can read.</p></div>"
    )
    return intro + block + outro


E["frameworks_html"] = fw_html()


def sec_build_db():
    body = (
        '<div class="prose"><p>We start with the database alone, before any web code exists. When something goes wrong later, it helps to know that the database part already works.</p></div>'
        + file_block(PROJECT, "setup_db.py", SETUP_CHUNKS, "python", "in vending-py/")
        + '<div class="prose"><p>You run it with <code>python setup_db.py</code>, and it prints the four rows that it stored:</p></div>'
        + snippet(
            "('A1', 'Sparkling Water', 175, 8)\n('A2', 'Salted Peanuts', 125, 5)\n('B1', 'Chocolate Bar', 200, 3)\n('B2', 'Oat Biscuits', 150, 0)",
            "text",
            "Output",
            copy=False,
        )
        + tryit(
            "<p>A new file called <code>vending.db</code> has appeared beside the script. That file is the whole database. Run the script a second time and think about what changed and why. Which line made the second run safe?</p>"
        ).replace("Try it", "A question to explore")
    )
    return section("build-db", "Part 7", "Build 1: the database on its own", body)


def sec_build_server():
    body = (
        '<div class="prose"><p>The server is the longest file, and it has a layered design. The <em>data layer</em> talks to the database and knows nothing about HTTP. '
        "The <em>route layer</em> connects URLs to data functions and checks input. The <em>HTTP layer</em> reads requests and writes responses, and the last lines start the server. "
        "Each layer uses only the one beneath it, so we can change one without disturbing the others. The file lists the layers in that order, and the explanations follow the same order.</p></div>"
        + layers_figure(E["layer_names"], E["slug"])
        + file_block(PROJECT, "server.py", SERVER_CHUNKS, "python", "in vending-py/")
        + '<div class="prose"><p>You start the server with <code>python server.py</code> and visit <code>http://127.0.0.1:8000/api/slots</code>. The browser shows a line of JSON. You have just used the API with no page and no script involved, and the terminal printed one log line for your request.</p></div>'
    )
    return section("build-server", "Part 8", "Build 2: the server and its API", body)


def sec_build_page():
    body = (
        '<div class="prose"><p>The page has two files and no logic. The HTML describes what exists, and the CSS describes how it looks. Before we read them, one idea needs a name. '
        "When a browser loads an HTML file it builds the <dfn>DOM</dfn> (Document Object Model), a tree of objects with one object for each element. The screen shows a drawing of that tree, and a script can change the tree. "
        "Changing the tree is how a server's answer reaches the screen.</p></div>"
        + file_block(PROJECT, "public/index.html", INDEX_CHUNKS, "html", "in vending-py/public/")
        + file_block(PROJECT, "public/style.css", CSS_CHUNKS, "css", "in vending-py/public/")
    )
    return section("build-page", "Part 9", "Build 3: the page, in HTML and CSS", body)


def sec_build_script():
    body = (
        '<div class="prose"><p>The script has one job: it asks the server for data, and it changes the page to match what the server says. A browser can run only JavaScript, so this part of the project is JavaScript, and it stays short on purpose. '
        "Everything with rules in it, such as the stock count and the validation, lives in the Python server.</p></div>"
        + file_block(PROJECT, "public/app.js", JS_CHUNKS, "javascript", "in vending-py/public/")
        + predict(
            "<p>When you press Buy, the script sends one request and gets one reply. Before you read Part 11, try to describe in your own words what the browser would show if the reply were slow, say five seconds. "
            "What does the visitor see during those five seconds, and how could we improve it?</p>"
        )
    )
    return section("build-script", "Part 10", "Build 4: the script that connects it all", body)


# ------------------------------------------------------- the browser demo

ADAPTER_CHUNKS = [
    ("", [], (
        "<p>This file is the whole of the new code. The docstring says why it exists: a browser cannot open a network port, so the bottom layer of our server, the one that reads from sockets, has no place to run. "
        "The two layers above it never needed sockets, so they run unchanged, and we write only a replacement for the top.</p>"
        "<p><code>import server</code> loads the real <code>server.py</code> from the project. Because of the <code>if __name__ == \"__main__\"</code> guard, importing it does not try to start a server.</p>"
    )),
    ("def answer", [4, 5, 8], (
        "<p>The function takes the method and the path, as the browser sent them, and returns a status code and the body text. The loop is the one from the real <code>answer_request</code>: it walks through the <code>ROUTES</code> table that the real file defines, "
        "and the first row whose method and pattern match calls the real handler. The data layer then runs real SQL against a real SQLite database, which here lives in the memory of the page.</p>"
    )),
    ("    # The same translation", [9], (
        "<p>These lines repeat the translation from exceptions to status codes, because that translation belonged to the HTTP layer that we replaced. "
        "A request for <code>B2</code>, which has no stock, ends here as a 409 with the same message that the real server sends.</p>"
    )),
]


def sec_try_first():
    body = (
        '<div class="prose"><p>Before you build anything, try the finished machine. It runs below, on this page, and you can press the buttons.</p></div>'
        '<figure class="demo"><iframe src="demo/vending.html" title="The vending machine page, answered by Python running in the browser" height="560" loading="lazy"></iframe>'
        "<figcaption>The vending machine. The page is the real one from the project, and a simulated server answers its requests. "
        "If nothing appears, open <a href=\"demo/vending.html\">the machine on its own page</a>.</figcaption></figure>"
        '<div class="prose"><h3>What is real here, and what is simulated</h3>'
        "<p>A web page cannot open a network port, so no real server program is running, and that is why this is a simulation. Three real things are running, though. "
        "<dfn>Pyodide</dfn> is the Python interpreter compiled into a form that browsers can run, and it runs the real <code>setup_db.py</code> and the real data layer and route table from <code>server.py</code>, including real SQL on a real SQLite database. "
        "The page's own script, <code>app.js</code>, is the file you will read in Part 10, with no changes. "
        "A <dfn>service worker</dfn>, which is a script that sits between a page and the network, notices each request whose address starts with <code>/api/</code>, and hands it to Python instead of sending it anywhere.</p>"
        "<p>The simulated part is the wire. No bytes travel between two programs, so Stations 3 and 9 of the journey are imitated, and the HTTP layer of the server is replaced by the short file below. "
        "That replacement is possible because we kept the layers apart, which is the reason for the design that Part 8 explains.</p></div>"
        + file_block(W / "demo-src", "py/adapter.py", ADAPTER_CHUNKS, "python", "the replacement for the HTTP layer")
        + tryit(
            "<p>Open the developer tools, choose the <strong>Network</strong> tab, reload the machine's own page, and press Buy. The rows for <code>/api/slots</code> show that a service worker answered, "
            "and the response headers include <code>X-Served-By</code>. Compare them with the real server's headers in Part 4: this reply has no <code>Server</code> or <code>Date</code> header, because no real server wrote it.</p>"
        )
        + '<div class="prose"><p>Do you want to change the pages, the SQL or the server, and then watch each request travel? The <a href="workbench/index.html">workbench</a> shows the browser, the server and the database side by side, with a timeline of every step.</p></div>'
        + '<div class="prose"><p>When you have played with the machine, carry on with the real thing. Part 11 starts a real server on your own computer, and the traffic you watch there is real traffic.</p></div>'
    )
    return section("try-first", "Try it first", "The finished machine, running in your browser", body)
