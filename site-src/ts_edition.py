"""TypeScript edition: edition values and the annotated builds."""

from pathlib import Path

from diagrams import layers_figure
from lib import box, file_block, predict, section, snippet, tryit
from py_edition import CSS_CHUNKS, INDEX_CHUNKS

W = Path(__file__).resolve().parent.parent
PROJECT = W / "vending-ts"

E = {
    "slug": "typescript",
    "shape_label_1": "selectOneSlot.get(slotId)",
    "shape_label_2": "JSON.stringify(slot)",
    "json_sample": '{"slot_id":"A1","item_name":"Sparkling Water","price_cents":175,"stock":7}',
    "name": "TypeScript",
    "proj": "vending-ts",
    "zip": "downloads/vending-ts.zip",
    "server_label": "A Node.js program",
    "record_word": "JavaScript object",
    "intro_languages": (
        "In this edition everything is TypeScript: the server, the setup script, the database code and the short script in the page. "
        "TypeScript is JavaScript with <dfn>types</dfn> added, which are labels that describe what kind of value each variable holds, so that a tool can catch mistakes before the program runs. "
        "The page itself uses plain HTML and CSS, and the script is about fifty lines of code."
    ),
    "prereq": (
        "You need Node.js 22.18 or newer, which includes npm, a terminal, a code editor, and a browser with developer tools. Chrome, Edge and Firefox all have them. "
        "From that version of Node onwards you can run a TypeScript file directly. The only packages you install are the TypeScript compiler and the type descriptions for Node, and you use both only while you develop."
    ),
    "http_status_line": "HTTP/1.1 200 OK",
    "http_status_note": (
        "<p>The first line of a response is the <dfn>status line</dfn>. It holds the protocol version, the <dfn>status code</dfn> and a short reason. "
        "Node answers in HTTP/1.1, the version that browsers use for most plain HTTP traffic, and the code 200 means success.</p>"
    ),
    "http_headers": (
        "Content-Type: application/json; charset=utf-8\n"
        "Content-Length: 74\n"
        "Cache-Control: no-store\n"
        "Date: Sat, 17 Oct 2026 21:55:29 GMT\n"
        "Connection: keep-alive\n"
        "Keep-Alive: timeout=5"
    ),
    "http_headers_extra": "The <code>Date</code>, <code>Connection</code> and <code>Keep-Alive</code> headers were added by Node without being asked. They tell the browser that it may reuse the same connection for its next request.",
    "json_colon": ":",
    "json_comma": ",",
    "contract_note": (
        "In this edition the contract appears twice in code, as a <code>Slot</code> type in the server and another in the page script. "
        "The compiler checks each program against its own copy, and it cannot see across the network, so if the two copies drift apart nothing warns you. "
        "That is a good reason to write the contract down in one more place, even if it is only a table like the one above."
    ),
    "shape2_title": "A JavaScript object in the server",
    "shape2_code": "{ slot_id: 'A1', item_name: 'Sparkling Water', price_cents: 175, stock: 7 }",
    "shape_step_1": "<code>selectOneSlot.get(slotId)</code> returns the row as an object",
    "shape_step_2": "<code>JSON.stringify(...)</code> serialises the object into text",
    "run_block": (
        "cd vending-ts\n"
        "npm install            # downloads the TypeScript compiler and Node's type descriptions\n"
        "npm run setup-db       # creates the database file\n"
        "npm run build          # compiles client/app.ts into public/app.js for the browser\n"
        "npm start              # starts the server and leaves it running"
    ),
    "run_note": box(
        "note",
        "A warning you will see",
        "<p>Node prints <code>ExperimentalWarning: SQLite is an experimental feature</code> when a program loads <code>node:sqlite</code>. "
        "It means that the Node team may still change the details of that module, and it does not mean that something is broken. "
        "We use the built-in module because it needs no installation, and the SQL you learn here is the same SQL that every other SQLite driver accepts.</p>",
    ),
    "log_sample": (
        "GET / 200\n"
        "GET /style.css 200\n"
        "GET /app.js 200\n"
        "GET /api/slots 200\n"
        "POST /api/slots/A1/buy 200"
    ),
    "injection_cmd": "node src/injection-demo.ts",
    "injection_output": (
        "The user typed: A1\n"
        "Joined into the string:\n"
        "  SQL sent to the database: SELECT item_name, stock FROM inventory WHERE slot_id = 'A1'\n"
        "  rows returned: 1\n"
        "Passed as a parameter:\n"
        "  SQL sent to the database: SELECT item_name, stock FROM inventory WHERE slot_id = ? with value \"A1\"\n"
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
    "rebuild_note": "Run <code>npm run build</code> afterwards, because the browser runs the compiled file and not your TypeScript. ",
    "cors_snippet": (
        '<code>"Access-Control-Allow-Origin": "http://127.0.0.1:9000"</code> '
        "inside the object that <code>sendBody</code> passes to <code>writeHead</code>, next to the other headers."
    ),
    "choice_server_title": "Node's built-in http module for the server, not a framework",
    "choice_server_why": "Every mechanism stays visible: reading the request, routing and writing the response. Nothing needs installing.",
    "choice_server_when": "In real projects, because a framework such as Express, Fastify or Hono supplies routing, validation, safe static files and many conveniences. The next section describes what they add.",
    "choice_conn_title": "One database connection for the whole program",
    "choice_conn_why": "Node runs our code on a single thread, so only one request touches the connection at a time, and the synchronous SQLite calls finish in microseconds. Sharing one connection also lets us prepare each statement once, at startup.",
    "choice_conn_when": "With a client-server database, every call crosses a network and takes time, so the calls are asynchronous (they use <code>await</code>) and the program keeps a pool of connections.",
    "body_hint": (
        "Node does not read the body for you. Collect the chunks with <code>for await (const chunk of request)</code>, join them, and parse the text with <code>JSON.parse</code>. "
        "That loop needs <code>await</code>, so <code>answerRequest</code> becomes an <code>async</code> function."
    ),
    "extra_extension": (
        "One type, shared.",
        "The <code>Slot</code> type is written twice, once in the server and once in the page script. "
        "Move it into a file that both can import, and discover what makes that harder than it sounds. Think about which program reads each import, and what a browser needs an import path to look like.",
    ),
    "sql_extra": "Node does not ship a SQLite shell, so these tools are the easiest route.",
    "static_server": "<code>npx http-server public -p 9000</code>",
    "handler_call": 'handleBuySlot("A1")',
    "route_row_flight": 'ROUTES entry:\n  { httpMethod: "POST", pathPattern: /^\\/api\\/slots\\/([^/]+)\\/buy$/, handler: handleBuySlot }\nhandleBuySlot("A1")',
    "validate_flight": 'validateSlotId("a1") returns "A1"',
    "layer_names": {
        "http": "answerRequest, sendJson, sendBody",
        "route": "ROUTES, handleBuySlot, validateSlotId",
        "data": "getAllSlots, getSlot, buySlot",
    },
}

# ------------------------------------------------------------ chunk texts

PACKAGE_CHUNKS = [
    ("", [], (
        "<p><code>package.json</code> is the identity card of a Node project. <code>private</code> stops us from publishing it to the public npm registry by accident. "
        "<code>\"type\": \"module\"</code> tells Node that our files use <code>import</code> and <code>export</code>, the modern module system, and not the older <code>require</code> style.</p>"
    )),
    ('  "scripts"', [], (
        "<p>Scripts are named shortcuts, run with <code>npm run name</code> (and <code>npm start</code> for the one called start). They record the exact commands that the project needs, so nobody has to remember them. "
        "<code>node src/server.ts</code> works because Node can run TypeScript directly, as the next page section explains. <code>tsc</code> is the TypeScript compiler. "
        "We use it twice: <code>check</code> only looks for type errors in the server files, and <code>build</code> turns the page script into JavaScript for the browser.</p>"
    )),
    ('  "devDependencies"', [], (
        "<p>These are the packages we need while we develop. There is no <code>dependencies</code> list at all, because the running server uses only what Node already contains. "
        "<code>typescript</code> is the compiler. <code>@types/node</code> is a set of descriptions of Node's built-in modules, written as types, so that the compiler knows what <code>node:http</code> and <code>node:sqlite</code> offer. "
        "The caret in <code>^7.0.2</code> allows newer versions that keep the same major number.</p>"
    )),
]

SETUP_CHUNKS = [
    ("", [], (
        "<p>The first lines say what the file is for and bring in two tools. Modules whose names start with <code>node:</code> are built into Node, so nothing needs installing. "
        "<code>path</code> builds file locations, and <code>DatabaseSync</code> is Node's driver for SQLite, which means a library that knows how to talk to one kind of database. "
        "The word <em>Sync</em> says that its calls wait for the database and return the answer directly, with no <code>await</code>.</p>"
        "<p>The database is a single file called <code>vending.db</code>. <code>import.meta.dirname</code> is the folder that holds this script, so the file lands in the project folder wherever you run the command from.</p>"
    )),
    ("// The schema describes", [7], (
        "<p>This text is the <dfn>schema</dfn>, written in SQL and stored in a template literal, which is a string in backticks that may run over several lines. <code>DROP TABLE IF EXISTS</code> deletes any old table, so running the script again resets the machine. "
        "That is convenient in a classroom and dangerous anywhere else, so the line deserves a pause.</p>"
        "<p><code>slot_id</code> is the <dfn>primary key</dfn>. The database refuses a second row with the same value, and it builds an index on the column so that lookups by slot are fast. "
        "The two <code>CHECK</code> lines are <dfn>constraints</dfn>, rules that the database enforces even when our own code has a bug. Money is stored as whole cents, for the reason given in Part 2.</p>"
    )),
    ("// Each entry is one row", [], (
        "<p>Our first TypeScript type: <code>[string, string, number, number][]</code> reads as <em>a list of rows, where each row is a group of two strings followed by two numbers</em>. "
        "If we wrote a price as text, or left out the stock, the compiler would mark the line before we ran anything. "
        "The Oat Biscuits start with zero stock on purpose, so that you can see a sold-out slot without buying everything first.</p>"
    )),
    ("// Opening the database", [6], (
        "<p>We open a <dfn>connection</dfn>. For SQLite this opens the file, and it creates the file if it does not exist yet. "
        "Then <code>BEGIN</code> starts a <dfn>transaction</dfn>, a group of steps that either all happen or none happen, and <code>exec</code> runs the schema. "
        "Node's SQLite is able to undo even a <code>DROP TABLE</code> and a <code>CREATE TABLE</code> inside a transaction, so the table creation and the inserts below stand or fall together.</p>"
    )),
    ("// A prepared statement", [6, 7], (
        "<p>A <dfn>prepared statement</dfn> is SQL that the database has read and checked once, and that we can then run many times. The question marks are <dfn>placeholders</dfn>: the SQL text and the values reach the database separately, "
        "and Experiment 3 in Part 12 shows why that matters. The three dots in <code>insertSlot.run(...slotRow)</code> spread the four values of a row into four arguments. "
        "After the loop, <code>COMMIT</code> ends the transaction and makes all four rows permanent.</p>"
    )),
    ("// Read the rows back", [6], (
        "<p>Finally we read the rows back so that you can see what was stored, and we close the connection. <code>all()</code> returns every matching row as an array of objects, and <code>Object.values</code> turns one object into the list of its values.</p>"
    )),
]

SERVER_CHUNKS = [
    ("", [3], (
        "<p>The comment at the top lists the four layers of the file, and the explanations below follow the same order. The imports bring in only what Node already contains. "
        "<code>readFileSync</code> reads a file from disk, <code>createServer</code> builds a web server, and <code>DatabaseSync</code> talks to SQLite. "
        "The line <code>import type</code> brings in two names that exist only as types, and it makes that fact visible.</p>"
        "<p>The <code>Slot</code> type describes one slot: it matches one row of the table and the JSON that we send. A type exists only while we write and check the program, and Node removes it before the program runs. "
        "So the type protects us from our own typing mistakes, and it does nothing about data that arrives from outside.</p>"
    )),
    ("// --- Settings", [3], (
        "<p>Names in capitals are constants, a convention for values that never change while the program runs. <code>HOST</code> decides who may connect, and <code>127.0.0.1</code> allows only your own computer, "
        "which is the safe choice while you develop. <code>PORT</code> decides which program receives the request.</p>"
        "<p><code>STATIC_FILES</code> is a <code>Map</code> of the only files that the server will send, each with a Content-Type. If it sent whatever file the URL named, a visitor could request a path such as <code>/../src/server.ts</code> and download our code and our database. "
        "That attack is called <dfn>path traversal</dfn>, and a fixed list prevents it. <code>SLOT_ID_PATTERN</code> is a <dfn>regular expression</dfn>, a compact pattern for text. This one means one capital letter followed by one digit.</p>"
    )),
    ("// --- Errors", [], (
        "<p>The program expects three kinds of trouble, and each one gets its own error class. The classes have no body of their own, because only their names matter.</p>"
        "<p>The data layer below never mentions HTTP. When something goes wrong it throws an error named in the vocabulary of the vending machine, and one place near the end of the file translates those names into status codes. "
        "That separation means we could reuse the data functions in a program that has no web server at all.</p>"
    )),
    ("// --- Data layer", [6], (
        "<p>We open one connection for the whole program. Node runs our code on a single thread, so only one request touches the connection at a time. "
        "The Python edition opens a new connection for every request because its server uses several threads.</p>"
        "<p>Every call on <code>database</code> is <dfn>synchronous</dfn>: the program waits for the answer and moves on. That would be a poor idea with a database on another computer, because the whole server would stall during each network trip. "
        "SQLite lives inside our own process and answers in microseconds, so waiting costs almost nothing.</p>"
    )),
    ("// A prepared statement is SQL that", [6, 7], (
        "<p>We prepare each statement once, when the server starts, and run it many times. If a table or column name were wrong, the error would appear at startup and not on the first click. "
        "The <code>?</code> is a placeholder for a value that travels separately from the SQL text, so a visitor can never change what the SQL means. That attack is called <dfn>SQL injection</dfn>.</p>"
        "<p>The third statement is the most important line in the file. We could have read the stock, tested it in JavaScript, and then written the new value. That plan leaves a gap, and two buyers who arrive together could both see a stock of 1 and both take the last item. "
        "The single <code>UPDATE</code> checks <code>stock &gt; 0</code> and subtracts in one indivisible step. The diagram in Part 13 compares the two plans.</p>"
    )),
    ("// Run some work as a transaction", [7], (
        "<p>This helper wraps any piece of work in <code>BEGIN</code> and <code>COMMIT</code>, and it calls <code>ROLLBACK</code> to undo everything if the work throws an error. The <code>throw error</code> inside <code>catch</code> passes the problem on, because the caller still needs to learn that the work failed. "
        "The Python edition gets the same behaviour from <code>with connection:</code>.</p>"
        "<p>The <code>&lt;T&gt;</code> is a <dfn>generic</dfn>. It means <em>whatever type the work returns</em>, and the function returns that same type, so a caller that passes work returning a <code>Slot</code> gets a <code>Slot</code> back.</p>"
    )),
    ("function getAllSlots", [6], (
        "<p>Two functions read data. The database cannot tell the compiler what its rows look like, so <code>as Slot[]</code> is a promise that we make: <em>trust us, these rows have the shape of a Slot</em>. The compiler accepts the promise without checking it.</p>"
        "<p>The method <code>get</code> returns a row or <code>undefined</code> when nothing matched, so the type is <code>Slot | undefined</code>. After the <code>=== undefined</code> test and the <code>throw</code>, the compiler knows that <code>slot</code> must be a real slot. "
        "TypeScript calls that <dfn>narrowing</dfn>, and it removes a whole family of <em>cannot read property of undefined</em> errors.</p>"
    )),
    ("// Take one item from a slot", [6, 7], (
        "<p>The work runs inside <code>runInTransaction</code>. First the single <code>UPDATE</code> tries to take one item, and its result says in <code>changes</code> how many rows it changed. "
        "Then we read the slot inside the same transaction, so that the numbers we report match the change we made, and <code>getSlot</code> throws <code>NoSuchSlot</code> if the slot does not exist.</p>"
        "<p>Zero changes with an existing slot can only mean that the stock was already zero, so we throw <code>SoldOut</code>. The error rolls the transaction back, which undoes nothing here because nothing changed, and it keeps the rule simple: any error undoes the work.</p>"
    )),
    ("// --- Route layer", [5], (
        "<p>Everything that comes from the URL is untrusted text. <code>validateSlotId</code> tidies it and checks that the whole text has the shape we expect, and it throws <code>BadRequest</code> when it does not. "
        "The queries are already safe from injection because they use parameters, so this check is a second layer. It gives a clear error early, and it keeps odd text out of our logs.</p>"
    )),
    ("function handleListSlots", [4], (
        "<p>The three handlers are deliberately thin. Each one connects a URL to a data function and validates the input on the way.</p>"
        "<p>A <code>Route</code> type describes one row of the table: a method, a pattern and a handler. The handler type says <em>a function that takes any number of text arguments and returns something</em>. "
        "<code>ROUTES</code> is the API written as data. In the patterns, <code>([^/]+)</code> means one or more characters that are not a slash, and the parentheses capture them, "
        "so the text between the slashes becomes an argument to the handler. Every web framework builds a table like this for you.</p>"
    )),
    ("// --- HTTP layer", [9], (
        "<p><code>sendBody</code> writes the response in the order that HTTP demands: the status line and the headers (<code>writeHead</code> writes both), a blank line, and the body (<code>end</code>). These are exactly the lines in the captured response in Part 4.</p>"
        "<p><code>Content-Length</code> counts bytes, and some characters take more than one byte, so we measure with <code>Buffer.byteLength</code> and not with <code>.length</code>. "
        "<code>sendJson</code> serialises the data with <code>JSON.stringify</code> and hands the text to <code>sendBody</code>. The type <code>unknown</code> for <code>data</code> means that we accept any value without making claims about it.</p>"
    )),
    ("// Node calls this function once", [4, 8, 9], (
        "<p>Node calls this function once for every request. It reads the method, and it takes the path out of <code>request.url</code> with the <code>URL</code> class, which also drops any query string. "
        "The <code>??</code> operator supplies a default when the left side is missing. A listener on the <code>finish</code> event prints one log line after the response has gone out.</p>"
        "<p>The function first checks whether the visitor asked for one of our three files. If not, it walks through <code>ROUTES</code>, and the first row whose method and pattern both match wins. "
        "The call <code>route.handler(...pathMatch.slice(1))</code> drops the whole match, keeps the captured text such as <code>\"A1\"</code>, and spreads it into arguments. Whatever the handler returns goes out as JSON with status 200.</p>"
        "<p>All of this sits inside a <code>try</code> block, so the <code>catch</code> is the one place where errors become status codes: 400, 404 and 409 for the three expected problems. "
        "Any other error is a bug of ours, so we print it for the developer and send a vague 500 to the client. Error details help attackers more than they help visitors, so they stay in the terminal.</p>"
    )),
    ("// Create the server and tell", [3], (
        "<p><code>createServer(answerRequest)</code> builds a server that calls our function for each request, and <code>listen</code> asks the operating system to deliver requests for that host and port. "
        "The function passed to <code>listen</code> runs once, when the server is ready. After that Node keeps the program alive, waiting for requests, until you press Ctrl+C.</p>"
    )),
]

SRC_TSCONFIG_CHUNKS = [
    ("", [], (
        "<p>This file configures the type checker for the server files. <code>target</code> names the version of JavaScript that we write, <code>module: NodeNext</code> follows the rules of Node's module system, and <code>lib</code> lists the built-in objects that the compiler may assume exist. "
        "We leave out the browser's objects such as <code>document</code>, because a server has none. <code>types: [\"node\"]</code> brings in the descriptions from <code>@types/node</code>.</p>"
    )),
    ('    "strict"', [], (
        "<p><code>strict</code> switches on the checks that catch the most mistakes, and it is the setting to use in every new project. "
        "<code>noUncheckedIndexedAccess</code> adds one more: reading <code>list[3]</code> gives a value that might be <code>undefined</code>, because the list might be shorter than you think.</p>"
    )),
    ('    "noEmit"', [], (
        "<p><code>noEmit</code> means that the compiler only checks and writes no files, because Node runs the TypeScript directly by stripping out the types. "
        "That is also why <code>erasableSyntaxOnly</code> is on. It forbids the few TypeScript features that need real translation, such as <code>enum</code>, so that deleting the types always leaves valid JavaScript behind. "
        "<code>verbatimModuleSyntax</code> asks us to write <code>import type</code> for imports that exist only as types, which is why <code>server.ts</code> uses it.</p>"
    )),
]

CLIENT_TSCONFIG_CHUNKS = [
    ("", [], (
        "<p>The script for the page needs different settings, so it has its own configuration. The browser understands <code>import</code> and <code>export</code>, so the module format stays modern. "
        "<code>moduleDetection: force</code> treats every file as a module, so names such as <code>Slot</code> stay private to the file and do not clash with the same name in the server.</p>"
    )),
    ('    "lib"', [], (
        "<p>Here the built-in objects include <code>DOM</code>, which describes <code>document</code>, <code>fetch</code> and every element type. <code>types</code> is empty on purpose, so Node's descriptions stay out and the compiler would flag any use of a Node-only function in browser code.</p>"
    )),
    ('    "strict"', [], (
        "<p>The same strict checking applies here. The setting <code>outDir</code> says where the compiled JavaScript goes: into <code>public</code>, beside the HTML, where the server can send it. "
        "A browser cannot run TypeScript, so <code>npm run build</code> is a required step for this file, and the server sends only the compiled <code>app.js</code>.</p>"
    )),
]

APP_CHUNKS = [
    ("", [], (
        "<p>The two types describe the JSON that the server sends. They are promises and not checks. The compiler uses them to help us write the rest of the script, and nothing compares them with the real reply while the page runs. "
        "If the server renamed <code>stock</code>, this file would still compile and the page would show <em>undefined left</em>. Part 5 explains why the contract between page and server needs to be written down.</p>"
    )),
    ("// Find an element by its id", [11], (
        "<p>The browser's <code>getElementById</code> returns an element or <code>null</code>. TypeScript makes us deal with the <code>null</code> before we use the result, so this helper stops with a clear message when the page lacks the element. "
        "After the check the compiler knows that a real element comes back.</p>"
    )),
    ("// Find the elements that we need", [11], (
        "<p>The three constants look up elements by their <code>id</code> and keep them in variables, so that we search the page once and not on every click. "
        "The phrase <code>as HTMLTemplateElement</code> tells the compiler a fact about our own page that it cannot see.</p>"
        "<p><code>Intl.NumberFormat</code> is a formatter that the browser provides. With the locale <code>en-IE</code> and the currency <code>EUR</code> it writes 1.75 as <code>€1.75</code>. "
        "We could have written <code>\"€\" + (cents / 100).toFixed(2)</code>, and that works until we meet a place whose conventions differ, so we let the formatter decide.</p>"
    )),
    ("// Send a request to our API", [2, 10], (
        "<p>This function wraps every API call, so the rest of the script never repeats the checks. Inside an <code>async</code> function, <code>await</code> pauses that function, and only that one, until a promise settles. "
        "The browser stays responsive meanwhile, which matters because a network reply can take a noticeable time. <code>fetch</code> sends the request at Station 2, and its reply arrives at Station 10.</p>"
        "<p>A call can fail in two different ways. When no response arrives at all, <code>fetch</code> itself rejects, and we turn that into a friendlier message. "
        "When a response arrives with a bad status such as 404 or 409, <code>fetch</code> counts it as success, because a reply did arrive, so we check <code>response.ok</code> ourselves and pass on the server's own message.</p>"
        "<p>The <code>&lt;T&gt;</code> lets each caller say what it expects: <code>requestJson&lt;Slot[]&gt;(...)</code>. The parsed JSON is typed <code>unknown</code>, which is the accurate type for data from outside, and the final <code>as T</code> is our promise that the server keeps its side of the contract.</p>"
    )),
    ("// Build one card for one slot", [11], (
        "<p>This function turns one slot, which is shape 4 in Part 6, into one card, which is shape 5. <code>cloneNode(true)</code> makes a deep copy of the template, so the template stays unchanged for the next card. "
        "The exclamation marks in this function say <em>this is never null</em>, because we wrote the template ourselves, and each one overrides the compiler's caution, so we use them only where we know the page.</p>"
        "<p>Notice <code>textContent</code> in every line that shows data. It treats the value as plain text. If we used <code>innerHTML</code> and an item name contained a script tag, the browser would run it, and that attack is called cross-site scripting. "
        "The function returns a card that is not on the screen yet, because nothing has attached it to the page.</p>"
    )),
    ("// Ask the server for every slot", [10, 11, 12], (
        "<p><code>slots.map(createSlotCard)</code> converts an array of data into an array of cards, and <code>replaceChildren(...)</code> swaps the contents of <code>#slots</code> for them in one step. "
        "That call is the moment when the DOM changes, and the browser repaints at Station 12. The <code>try</code> and <code>catch</code> show any error message in the status line, so the visitor sees what went wrong. "
        "Inside <code>catch</code> the error has the type <code>unknown</code>, so we state what it is with <code>as Error</code>.</p>"
    )),
    ("// One listener on the whole list", [1, 2, 10, 11], (
        "<p>We attach one listener to the container and not one to each button, because the buttons do not exist yet when this line runs. A click on a button <dfn>bubbles</dfn> up through its parents, so the container hears it. "
        "This technique is called <dfn>event delegation</dfn>, and <code>closest</code> climbs from the clicked element to the nearest Buy button, or returns <code>null</code> when the click landed elsewhere.</p>"
        "<p>This function is Station 1. We read the slot id back from <code>slotCard.dataset.slot</code>, send a <code>POST</code> request, and swap in a new card made from the server's reply. "
        "We draw what the server said and not what we guess, so if another person bought the last item a moment earlier, the card tells the truth.</p>"
    )),
    ("// Show the slots as soon", [2], (
        "<p>The last line runs once when the script loads, and it sends the first request.</p>"
    )),
]

# ------------------------------------------------------------- sections


def fw_html():
    return (
        '<div class="prose"><h3>Where frameworks fit</h3>'
        "<p>In a real project you would rarely write the plumbing of a server by hand. A <dfn>framework</dfn> provides routing, input validation, safe static file serving, error handling and many conveniences, "
        "and it lets you write only the parts that are particular to your application. We built the plumbing ourselves so that each mechanism is visible once.</p>"
        "<p>The usual names in the Node world are Express, which is the oldest and most widely taught, Fastify, which adds validation from a schema and is built for speed, and Hono, which is small and runs on many platforms. "
        "In each of them our route table would shrink to three lines such as <em>on GET /api/slots, call this function</em>, and the framework would read the request, set the headers and send the JSON. "
        "All of them sit on top of the same <code>node:http</code> module that we used, so what you learned here is what they do underneath.</p></div>"
    )


E["frameworks_html"] = fw_html()


def sec_build_db():
    body = (
        '<div class="prose"><p>We start with the database alone, before any web code exists. When something goes wrong later, it helps to know that the database part already works. '
        "First, two things about TypeScript need a name, because they shape how every command on this page works.</p>"
        "<h3>Types are labels that disappear</h3>"
        "<p>A <dfn>type</dfn> says what kind of value a variable holds, for example a number or a text. When we write <code>price_cents: number</code> we add a label, and a tool called the <dfn>type checker</dfn> reads those labels and reports mistakes such as adding a number to a text before the program ever runs. "
        "The labels exist only for the checker. Before the program runs they are erased, and what remains is ordinary JavaScript.</p>"
        "<h3>Running TypeScript</h3>"
        "<p>Node 22.18 and newer can run a TypeScript file directly, by erasing the labels as it loads the file. That is called <dfn>type stripping</dfn>, and it is why <code>node src/server.ts</code> works with no build step. "
        "A browser cannot do this, so the script for the page goes through the compiler, <code>tsc</code>, which writes a JavaScript file. The server files use stripping, and the page script uses the compiler.</p></div>"
        + file_block(PROJECT, "package.json", PACKAGE_CHUNKS, "json", "in vending-ts/")
        + file_block(PROJECT, "src/setup-db.ts", SETUP_CHUNKS, "typescript", "in vending-ts/src/")
        + '<div class="prose"><p>You run it with <code>npm run setup-db</code>, and it prints the four rows that it stored, after the experimental warning:</p></div>'
        + snippet(
            "[ 'A1', 'Sparkling Water', 175, 8 ]\n[ 'A2', 'Salted Peanuts', 125, 5 ]\n[ 'B1', 'Chocolate Bar', 200, 3 ]\n[ 'B2', 'Oat Biscuits', 150, 0 ]",
            "text",
            "Output",
            copy=False,
        )
        + tryit(
            "<p>A new file called <code>vending.db</code> has appeared in the project folder. That file is the whole database. Run the script a second time and think about what changed and why. Which line made the second run safe?</p>"
        ).replace("Try it", "A question to explore")
    )
    return section("build-db", "Part 7", "Build 1: the database on its own", body)


def sec_build_server():
    body = (
        '<div class="prose"><p>The server is the longest file, and it has a layered design. The <em>data layer</em> talks to the database and knows nothing about HTTP. '
        "The <em>route layer</em> connects URLs to data functions and checks input. The <em>HTTP layer</em> reads requests and writes responses, and the last lines start the server. "
        "Each layer uses only the one beneath it, so we can change one without disturbing the others. The file lists the layers in that order, and the explanations follow the same order.</p></div>"
        + layers_figure(E["layer_names"], E["slug"])
        + file_block(PROJECT, "src/server.ts", SERVER_CHUNKS, "typescript", "in vending-ts/src/")
        + file_block(PROJECT, "src/tsconfig.json", SRC_TSCONFIG_CHUNKS, "json", "in vending-ts/src/")
        + '<div class="prose"><p>Type <code>npm run check</code> to ask the type checker to read the server files. It prints nothing when it finds no problem. '
        "You start the server with <code>npm start</code> and visit <code>http://127.0.0.1:8000/api/slots</code>, once the page script has been built as Part 10 describes. "
        "The browser shows a line of JSON. You have just used the API with no page and no script involved, and the terminal printed one log line for your request.</p></div>"
    )
    return section("build-server", "Part 8", "Build 2: the server and its API", body)


def sec_build_page():
    body = (
        '<div class="prose"><p>The page has two files and no logic, and they are identical in both editions of this tutorial. The HTML describes what exists, and the CSS describes how it looks. Before we read them, one idea needs a name. '
        "When a browser loads an HTML file it builds the <dfn>DOM</dfn> (Document Object Model), a tree of objects with one object for each element. The screen shows a drawing of that tree, and a script can change the tree. "
        "Changing the tree is how a server's answer reaches the screen.</p></div>"
        + file_block(PROJECT, "public/index.html", INDEX_CHUNKS, "html", "in vending-ts/public/")
        + file_block(PROJECT, "public/style.css", CSS_CHUNKS, "css", "in vending-ts/public/")
    )
    return section("build-page", "Part 9", "Build 3: the page, in HTML and CSS", body)


def sec_build_script():
    body = (
        '<div class="prose"><p>The script has one job: it asks the server for data, and it changes the page to match what the server says. '
        "Everything with rules in it, such as the stock count and the validation, lives in the server. The script is TypeScript too, so the compiler checks it against the browser's own descriptions of the page.</p></div>"
        + file_block(PROJECT, "client/app.ts", APP_CHUNKS, "typescript", "in vending-ts/client/")
        + file_block(PROJECT, "client/tsconfig.json", CLIENT_TSCONFIG_CHUNKS, "json", "in vending-ts/client/")
        + '<div class="prose"><p>Run <code>npm run build</code> and the compiler writes <code>public/app.js</code>. Open it and compare it with the TypeScript. This is the start of the function that sends requests, before and after:</p></div>'
        + snippet(
            "async function requestJson<T>(url: string, options?: RequestInit): Promise<T> {\n  let response: Response;",
            "typescript",
            "Before: client/app.ts",
            copy=False,
        )
        + snippet(
            "async function requestJson(url, options) {\n    let response;",
            "javascript",
            "After: public/app.js",
            copy=False,
        )
        + '<div class="prose"><p>Every label has gone and the logic is untouched. The file in <code>public</code> is generated, so you never edit it by hand: change the TypeScript, run <code>npm run build</code>, and reload the page.</p></div>'
        + predict(
            "<p>When you press Buy, the script sends one request and gets one reply. Before you read Part 11, try to describe in your own words what the browser would show if the reply were slow, say five seconds. "
            "What does the visitor see during those five seconds, and how could we improve it?</p>"
        )
    )
    return section("build-script", "Part 10", "Build 4: the script that connects it all", body)


# ------------------------------------------------------- the browser demo

SHIM_CHUNKS = [
    ("", [], (
        "<p>Node has a built-in SQLite module, <code>node:sqlite</code>, and a browser has no such module. <dfn>sql.js</dfn> is the SQLite engine compiled into WebAssembly, a compact format that browsers run, and it gives us a real SQLite database inside the page. "
        "Its methods have different names from Node's, so this file wraps sql.js in the small interface that <code>server.ts</code> expects.</p>"
        "<p>The map keeps each database in memory under a file name. Opening the same name twice returns the same database, which is how the setup script and the server end up sharing one machine, as they share <code>vending.db</code> on disk.</p>"
    )),
    ("class StatementSync", [6], (
        "<p>A statement object holds one piece of SQL. The constructor prepares it at once, so a mistake in the SQL fails when the server starts and not on the first click, as with the real module.</p>"
    )),
    ("  // Return every matching row", [6], (
        "<p><code>all</code> runs the statement with the values that the caller passes, and it collects the rows into an array of objects. The values travel separately from the SQL text, so the placeholders protect this demo from injection in the same way as the real server. "
        "The <code>finally</code> block frees the statement even when something goes wrong, because sql.js keeps statements in memory until we release them. <code>get</code> is <code>all</code> with only the first row kept.</p>"
    )),
    ("  // Run a statement that changes data", [7], (
        "<p><code>run</code> executes a statement that changes data. SQLite counts the rows that the statement changed, and we return that count under the name <code>changes</code>, the name that <code>buySlot</code> in <code>server.ts</code> reads to find out whether the purchase worked.</p>"
    )),
    ("class DatabaseSync", [6], (
        "<p>The database class has only the three methods that our code calls. <code>exec</code> runs SQL, <code>prepare</code> makes a statement, and <code>close</code> does nothing, because a closed in-memory database could never be reopened.</p>"
    )),
]

ADAPTER_CHUNKS = [
    ("", [], (
        "<p>This file is typed, like the rest of the project. The <code>Machine</code> type lists the four things that the adapter takes from <code>server.ts</code>: the route table and the three error classes. "
        "The comment at the top says why the adapter exists. The real HTTP layer uses <code>node:http</code>, which needs a network, so we write a replacement for that layer only.</p>"
    )),
    ("function createAnswerer", [4], (
        "<p>The function receives the machine and returns an <code>answer</code> function, which takes a method and a path and returns a status and a body. That is the whole job of an HTTP layer, once the network part is removed.</p>"
    )),
    ("      // The same route table", [4, 8], (
        "<p>The loop is the one from the real <code>answerRequest</code>. It walks through the <code>ROUTES</code> table that <code>server.ts</code> defines, and the first row whose method and pattern match calls the real handler. "
        "The data layer then runs real SQL against a real SQLite database, which here lives in the memory of the page.</p>"
    )),
    ("      // The same translation", [9], (
        "<p>These lines repeat the translation from errors to status codes, because that translation belonged to the layer that we replaced. A request for <code>B2</code>, which has no stock, ends here as a 409 with the same message that the real server sends.</p>"
    )),
]


def sec_try_first():
    body = (
        '<div class="prose"><p>Before you build anything, try the finished machine. It runs below, on this page, and you can press the buttons.</p></div>'
        '<figure class="demo"><iframe src="demo-ts/vending.html" title="The vending machine page, answered by TypeScript running in the browser" height="560" loading="lazy"></iframe>'
        '<figcaption>The vending machine. The page is the real one from the project, and a simulated server answers its requests. '
        'If nothing appears, open <a href="demo-ts/vending.html">the machine on its own page</a>.</figcaption></figure>'
        '<div class="prose"><h3>What is real here, and what is simulated</h3>'
        "<p>A web page cannot open a network port, so no real server program is running, and that is why this is a simulation. Four real things are running, though. "
        "The data layer and the route table are copied out of the real <code>server.ts</code> when this page is built, with the types removed, so they are the same code that you will read in Part 8. "
        "The real <code>setup-db.ts</code> creates the table. <dfn>sql.js</dfn> supplies a real SQLite database that lives in the memory of the page. "
        "The page's own script, compiled from <code>client/app.ts</code>, is the file you will read in Part 10. "
        "A <dfn>service worker</dfn>, which is a script that sits between a page and the network, notices each request whose address starts with <code>/api/</code>, and hands it to the code above instead of sending it anywhere.</p>"
        "<p>The simulated part is the wire. No bytes travel between two programs, so Stations 3 and 9 of the journey are imitated. Two small files stand in for what a browser lacks: a wrapper that gives sql.js the interface of Node's SQLite module, and a replacement for the HTTP layer. "
        "Both are short, and the second is possible because we kept the layers apart, which is the reason for the design that Part 8 explains.</p></div>"
        + file_block(W / "demo-src", "ts/node-sqlite-shim.js", SHIM_CHUNKS, "javascript", "the stand-in for node:sqlite")
        + file_block(W / "demo-src", "ts/adapter.ts", ADAPTER_CHUNKS, "typescript", "the replacement for the HTTP layer")
        + tryit(
            "<p>Open the developer tools, choose the <strong>Network</strong> tab, reload the machine's own page, and press Buy. The rows for <code>/api/slots</code> show that a service worker answered, "
            "and the response headers include <code>X-Served-By</code>. Compare them with the real server's headers in Part 4: this reply has no <code>Date</code> or <code>Connection</code> header, because no real server wrote it.</p>"
        )
        + '<div class="prose"><p>Do you want to change the pages, the SQL or the server, and then watch each request travel? The <a href="workbench/index.html">workbench</a> shows the browser, the server and the database side by side, with a timeline of every step.</p></div>'
        + '<div class="prose"><p>When you have played with the machine, carry on with the real thing. Part 11 starts a real server on your own computer, and the traffic you watch there is real traffic.</p></div>'
    )
    return section("try-first", "Try it first", "The finished machine, running in your browser", body)
