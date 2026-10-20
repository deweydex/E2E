"""TypeScript edition: edition values and the annotated builds."""

from pathlib import Path

from diagrams import layers_figure
from lib import box, check, deeper, file_block, goal, make_steps, predict, section, snippet, tryit
from py_edition import CSS_CHUNKS, INDEX_CHUNKS
from shared_a import concept_database, concept_server, concept_shapes

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
        "In this edition everything is TypeScript: the server, the setup script, the database code and the page's script. "
        "TypeScript is JavaScript with <dfn>types</dfn> added, which are labels that say what kind of value each variable holds, so that a tool can catch mistakes before the program runs. "
        "The page itself is plain HTML and CSS, and the script is about fifty lines."
    ),
    "needs": [
        "Node.js 22.18 or newer, which includes npm. From that version Node can run a TypeScript file directly.",
        "A terminal and a code editor.",
        "A browser with developer tools. Chrome, Edge and Firefox all have them.",
        "Two packages, installed with npm: the TypeScript compiler and the type descriptions for Node. You use both only while you develop.",
    ],
    "http_status_line": "HTTP/1.1 200 OK",
    "http_status_note": (
        "<p>The <dfn>status line</dfn> holds the protocol version, the <dfn>status code</dfn> and a short reason. "
        "Node answers in HTTP/1.1, the version browsers use for most plain HTTP traffic. The code 200 means success.</p>"
    ),
    "http_headers": (
        "Content-Type: application/json; charset=utf-8\n"
        "Content-Length: 74\n"
        "Cache-Control: no-store\n"
        "Date: Sat, 17 Oct 2026 21:55:29 GMT\n"
        "Connection: keep-alive\n"
        "Keep-Alive: timeout=5"
    ),
    "http_headers_extra": "Node added the <code>Date</code>, <code>Connection</code> and <code>Keep-Alive</code> headers without being asked. They tell the browser it may reuse the same connection for its next request.",
    "json_colon": ":",
    "json_comma": ",",
    "contract_note": (
        "In this edition the contract appears twice in code, as a <code>Slot</code> type in the server and another in the page script. "
        "Each copy is checked only against its own program, so if they drift apart nothing warns you. A table like the one above gives both a single reference."
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
        "The warning means that the Node team may still change the details of that module. It does not mean that something is broken. "
        "We use the built-in module because that module needs no installation, and the SQL you learn here is the same SQL that every other SQLite driver accepts.</p>",
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
        "Move the type into a file that both can import, and discover what makes that harder than it sounds. Think about which program reads each import, and what a browser needs an import path to look like.",
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
        "<ul>"
        "<li><code>package.json</code> is the identity card of a Node project.</li>"
        "<li><code>private</code> stops you from publishing the project to the public npm registry (the shared online store of packages) by accident.</li>"
        "<li><code>\"type\": \"module\"</code> tells Node that our files use <code>import</code> and <code>export</code>, the modern module system.</li>"
        "</ul>"
    )),
    ('  "scripts"', [], (
        "<p>Scripts are named shortcuts, run with <code>npm run name</code> (and <code>npm start</code> for the one called start). They record the exact commands the project needs, so nobody has to remember them.</p>"
        "<ul>"
        "<li><code>node src/server.ts</code> works because Node can run TypeScript directly.</li>"
        "<li><code>tsc</code> is the TypeScript compiler. <code>check</code> only looks for type errors in the server files, and <code>build</code> turns the page script into JavaScript for the browser.</li>"
        "</ul>"
    )),
    ('  "devDependencies"', [], (
        "<ul>"
        "<li>These packages are needed only while you develop. There is no <code>dependencies</code> list, because the running server uses only what Node already contains.</li>"
        "<li><code>typescript</code> is the compiler.</li>"
        "<li><code>@types/node</code> describes Node's built-in modules as types, so the compiler knows what <code>node:http</code> and <code>node:sqlite</code> offer.</li>"
        "<li>The caret in <code>^7.0.2</code> allows newer versions with the same first (major) number, so 7.1 is allowed and 8.0 is not.</li>"
        "</ul>"
    )),
]

SETUP_CHUNKS = [
    ("", [], (
        "<p>The top of the file says what it is for and imports two tools.</p>"
        "<ul>"
        "<li>Modules named <code>node:...</code> are built into Node, so nothing needs installing.</li>"
        "<li><code>path</code> builds file locations. <code>DatabaseSync</code> is Node's driver for SQLite, a library that knows how to talk to one kind of database.</li>"
        "<li><em>Sync</em> means its calls wait for the database and return the answer directly, with no <code>await</code>. (<code>await</code> is how JavaScript waits for something slow. Step 5 explains it.)</li>"
        "<li>The database is one file, <code>vending.db</code>. <code>import.meta.dirname</code> is the folder that holds this script, so the file lands in the project folder wherever you run the command from.</li>"
        "</ul>"
    )),
    ("// The schema describes", [7], (
        "<p>This text is the <dfn>schema</dfn>, written in SQL inside a template literal, a string in backticks that may run over several lines.</p>"
        "<ul>"
        "<li><code>DROP TABLE IF EXISTS</code> deletes any old table, so running the script again resets the machine. That is handy in a classroom and dangerous anywhere else.</li>"
        "<li><code>slot_id</code> is the primary key. The database refuses a second row with the same value and builds an index for fast lookups.</li>"
        "<li>The two <code>CHECK</code> lines are constraints. The database enforces them even when our code has a bug.</li>"
        "<li>Money is stored as whole cents.</li>"
        "</ul>"
    )),
    ("// Each entry is one row", [], (
        "<p>This is our first TypeScript type. <code>[string, string, number, number][]</code> reads as <em>a list of rows, each a group of two strings followed by two numbers</em>. "
        "If we wrote a price as text or left out the stock, the compiler would mark the line before we ran anything.</p>"
        "<p>The Oat Biscuits start with zero stock on purpose, so that you can see a sold-out slot without buying everything first.</p>"
    )),
    ("// Opening the database", [6], (
        "<ul>"
        "<li>We open a <dfn>connection</dfn>. For SQLite this opens the file, and creates it if it does not exist yet.</li>"
        "<li><code>BEGIN</code> starts a <dfn>transaction</dfn>, and <code>exec</code> runs the schema.</li>"
        "<li>Node's SQLite can undo even a <code>DROP TABLE</code> and a <code>CREATE TABLE</code> inside a transaction, so the table and the inserts below stand or fall together.</li>"
        "</ul>"
    )),
    ("// A prepared statement", [6, 7], (
        "<p>A <dfn>prepared statement</dfn> is SQL that the database has read and checked once, and that we can then run many times.</p>"
        "<ul>"
        "<li>The question marks are <dfn>placeholders</dfn>. The SQL text and the values reach the database separately, and the experiments after Step 6 show why that matters.</li>"
        "<li>The three dots in <code>insertSlot.run(...slotRow)</code> spread the four values of a row into four arguments.</li>"
        "<li>After the loop, <code>COMMIT</code> makes all four rows permanent.</li>"
        "</ul>"
    )),
    ("// Read the rows back", [6], (
        "<p>Finally we read the rows back to see what was stored, and close the connection. <code>all()</code> returns every matching row as an array of objects, and <code>Object.values</code> turns one object into the list of its values.</p>"
    )),
]

SERVER_CHUNKS = [
    ("", [3], (
        "<p>The comment at the top lists the four layers of the file, and the explanations follow the same order.</p>"
        "<ul>"
        "<li>The imports bring in only what Node already contains: <code>readFileSync</code> reads a file, <code>createServer</code> builds a web server, and <code>DatabaseSync</code> talks to SQLite.</li>"
        "<li><code>import type</code> brings in two names that exist only as types, and makes that visible.</li>"
        "<li>The <code>Slot</code> type describes one slot. The type matches one row of the table and the JSON we send.</li>"
        "<li>A type exists only while you write and check the program, and Node removes the type before the program runs. So a type protects you from your own typing mistakes and does nothing about data that arrives from outside.</li>"
        "</ul>"
    )),
    ("// --- Settings", [3], (
        "<ul>"
        "<li>Names in capitals are constants, a convention for values that never change while the program runs.</li>"
        "<li><code>HOST</code> decides who may connect. <code>127.0.0.1</code> allows only your own computer, which is the safe choice while you develop.</li>"
        "<li><code>PORT</code> decides which program receives the request.</li>"
        "<li><code>STATIC_FILES</code> is a <code>Map</code> (a collection of key and value pairs) of the only files the server will send. If the server sent whatever file the URL named, a visitor could ask for <code>/../src/server.ts</code> and download our code and our database. That attack is <dfn>path traversal</dfn>.</li>"
        "<li><code>SLOT_ID_PATTERN</code> is a <dfn>regular expression</dfn>, a compact pattern for text. This one means one capital letter followed by one digit.</li>"
        "</ul>"
    )),
    ("// --- Errors", [], (
        "<p>The program expects three kinds of trouble, and each gets its own error class. The classes have no body, because only their names matter.</p>"
        "<p>The data layer never mentions HTTP. When something goes wrong it throws an error named after what went wrong in the machine, such as <code>SoldOut</code>, and one place near the end of the file turns those names into status codes. "
        "So we could reuse the data functions in a program that has no web server at all.</p>"
    )),
    ("// --- Data layer", [6], (
        "<ul>"
        "<li>We open one connection for the whole program. Node runs our code on a single thread, so only one request touches the connection at a time. (The Python edition opens one per request because its server uses several threads.)</li>"
        "<li>Every call on <code>database</code> is <dfn>synchronous</dfn>: the program waits for the answer and moves on.</li>"
        "<li>That would be a poor idea with a database on another computer, because the whole server would stall during each network trip. SQLite lives inside our own process and answers in microseconds, so waiting costs almost nothing.</li>"
        "</ul>"
    )),
    ("// A prepared statement is SQL that", [6, 7], (
        "<ul>"
        "<li>We prepare each statement once, when the server starts, and run it many times. A wrong table or column name shows up at startup and not on the first click.</li>"
        "<li>The <code>?</code> is a placeholder for a value that travels separately from the SQL, so a visitor can never change what the SQL means. That attack is <dfn>SQL injection</dfn>.</li>"
        "<li>The third statement is the most important line in the file. We could read the stock, test it in JavaScript and write the new value, but that leaves a gap in which two buyers could both take the last item.</li>"
        "<li>The single <code>UPDATE</code> checks <code>stock &gt; 0</code> and subtracts in one indivisible step. The section on design choices compares the two plans in a diagram.</li>"
        "</ul>"
    )),
    ("// Run some work as a transaction", [7], (
        "<ul>"
        "<li>This helper wraps any piece of work in <code>BEGIN</code> and <code>COMMIT</code>, and calls <code>ROLLBACK</code> to undo everything if the work throws.</li>"
        "<li><code>throw error</code> inside <code>catch</code> passes the problem on, because the caller still needs to learn that the work failed.</li>"
        "<li>The Python edition gets the same behaviour from <code>with connection:</code>.</li>"
        "<li><code>&lt;T&gt;</code> is a <dfn>generic</dfn>: <em>whatever type the work returns</em>. Work that returns a <code>Slot</code> gives a <code>Slot</code> back.</li>"
        "</ul>"
    )),
    ("function getAllSlots", [6], (
        "<p>Two functions read data.</p>"
        "<ul>"
        "<li>The database cannot tell the compiler what its rows look like, so <code>as Slot[]</code> is our claim: <em>these rows have the shape of a Slot</em>. The compiler accepts that claim without checking.</li>"
        "<li><code>get</code> returns a row or <code>undefined</code>, so the type is <code>Slot | undefined</code>. After the <code>=== undefined</code> test and the <code>throw</code>, the compiler knows <code>slot</code> is a real slot. TypeScript calls this <dfn>narrowing</dfn>, and it removes a whole family of <em>cannot read property of undefined</em> errors.</li>"
        "</ul>"
    )),
    ("// Take one item from a slot", [6, 7], (
        "<ul>"
        "<li>The work runs inside <code>runInTransaction</code>. First the single <code>UPDATE</code> tries to take one item, and <code>changes</code> says how many rows it changed.</li>"
        "<li>Then we read the slot inside the same transaction, so the numbers we report match the change we made. <code>getSlot</code> throws <code>NoSuchSlot</code> if the slot does not exist.</li>"
        "<li>Zero changes with an existing slot can only mean the stock was already zero, so we throw <code>SoldOut</code>. The rule stays simple: any error undoes the work.</li>"
        "</ul>"
    )),
    ("// --- Route layer", [5], (
        "<p>Everything that comes from the URL is untrusted text. <code>validateSlotId</code> cleans up that text (turning <code>a1</code> into <code>A1</code>), checks that the whole text has the expected shape, and throws <code>BadRequest</code> if not.</p>"
        "<p>The queries are already safe from SQL injection because they use parameters. This check is a second layer that gives a clear error early and keeps odd text out of our logs.</p>"
    )),
    ("function handleListSlots", [4], (
        "<p>The three handlers are thin. Each connects a URL to a data function and validates the input on the way.</p>"
        "<ul>"
        "<li>The <code>Route</code> type describes one row of the table: a method, a pattern and a handler. A handler is <em>a function that takes any number of text arguments and returns something</em>.</li>"
        "<li><code>ROUTES</code> is the API written as data.</li>"
        "<li>In a pattern, <code>([^/]+)</code> means one or more characters that are not a slash. The parentheses capture them, so the text between the slashes becomes an argument to the handler.</li>"
        "<li>Every web framework builds a table like this for you.</li>"
        "</ul>"
    )),
    ("// --- HTTP layer", [9], (
        "<ul>"
        "<li><code>sendBody</code> writes the response in the order HTTP demands: the status line and headers (<code>writeHead</code> writes both), a blank line, and the body (<code>end</code>).</li>"
        "<li><code>Content-Length</code> counts bytes, and some characters take more than one, so we measure with <code>Buffer.byteLength</code> and not <code>.length</code>.</li>"
        "<li><code>sendJson</code> turns the data into text with <code>JSON.stringify</code> and hands the text to <code>sendBody</code>.</li>"
        "<li>The type <code>unknown</code> for <code>data</code> means we accept any value without making claims about it.</li>"
        "</ul>"
    )),
    ("// Node calls this function once", [4, 8, 9], (
        "<ul>"
        "<li>Node calls this function once for every request. The function reads the method and takes the path out of <code>request.url</code> with the <code>URL</code> class, which also separates the path from any query string (the <code>?name=value</code> part).</li>"
        "<li><code>??</code> supplies a default when the left side is missing. A listener on <code>finish</code> prints one log line after the response has gone out.</li>"
        "<li>The function first checks whether the visitor asked for one of our three files. If not, the function walks through <code>ROUTES</code>, and the first row whose method and pattern both match wins.</li>"
        "<li><code>route.handler(...pathMatch.slice(1))</code> drops the whole match, keeps the captured text such as <code>\"A1\"</code>, and spreads it into arguments. Whatever the handler returns goes out as JSON with status 200.</li>"
        "<li>The <code>catch</code> is the one place where errors become status codes: 400, 404 and 409.</li>"
        "<li>Any other error is our own bug. We print the error for the developer and send a vague 500, because error details help attackers more than visitors.</li>"
        "</ul>"
    )),
    ("// Create the server and tell", [3], (
        "<p><code>createServer(answerRequest)</code> builds a server that calls our function for each request. <code>listen</code> asks the operating system to deliver requests for that host and port.</p>"
        "<p>The function passed to <code>listen</code> runs once, when the server is ready. After that Node keeps the program alive until you press Ctrl+C.</p>"
    )),
]

SRC_TSCONFIG_CHUNKS = [
    ("", [], (
        "<p>This file configures the type checker for the server files.</p>"
        "<ul>"
        "<li><code>target</code> names the version of JavaScript we write.</li>"
        "<li><code>module: NodeNext</code> follows the rules of Node's module system.</li>"
        "<li><code>lib</code> lists the built-in objects the compiler may assume exist. We leave out the browser's objects such as <code>document</code>, because a server has none.</li>"
        "<li><code>types: [\"node\"]</code> brings in the descriptions from <code>@types/node</code>.</li>"
        "</ul>"
    )),
    ('    "strict"', [], (
        "<p><code>strict</code> switches on the checks that catch the most mistakes. Use that setting in every new project.</p>"
        "<p><code>noUncheckedIndexedAccess</code> adds one more: reading <code>list[3]</code> gives a value that might be <code>undefined</code>, because the list might be shorter than you think.</p>"
    )),
    ('    "noEmit"', [], (
        "<ul>"
        "<li><code>noEmit</code> means the compiler only checks and writes no files, because Node runs the TypeScript directly by stripping out the types.</li>"
        "<li><code>erasableSyntaxOnly</code> forbids the few TypeScript features that need real translation, such as <code>enum</code> (a named set of constants), so deleting the types always leaves valid JavaScript.</li>"
        "<li><code>verbatimModuleSyntax</code> asks us to write <code>import type</code> for imports that exist only as types.</li>"
        "</ul>"
    )),
]

CLIENT_TSCONFIG_CHUNKS = [
    ("", [], (
        "<p>The page script needs different settings, so it has its own configuration.</p>"
        "<ul>"
        "<li>Browsers understand <code>import</code> and <code>export</code>, so the module format stays modern.</li>"
        "<li><code>moduleDetection: force</code> treats every file as a module, so names such as <code>Slot</code> stay private to the file and do not clash with the server's.</li>"
        "</ul>"
    )),
    ('    "lib"', [], (
        "<p>Here the built-in objects include <code>DOM</code>, which describes <code>document</code>, <code>fetch</code> and every element type. <code>types</code> is empty on purpose, so Node's descriptions stay out and the compiler flags any Node-only function used in browser code.</p>"
    )),
    ('    "strict"', [], (
        "<p>The same strict checking applies. <code>outDir</code> says where the compiled JavaScript goes: into <code>public</code>, beside the HTML, where the server can send it.</p>"
        "<p>A browser cannot run TypeScript, so <code>npm run build</code> is required for this file, and the server sends only the compiled <code>app.js</code>.</p>"
    )),
]

APP_CHUNKS = [
    ("", [], (
        "<p>The two types describe the JSON the server sends. They are claims and not checks: the compiler uses them to help us write the rest of the script, and nothing compares them with the real reply while the page runs.</p>"
        "<p>If the server renamed <code>stock</code>, this file would still compile and the page would show <em>undefined left</em>. That is why the contract between page and server needs to be written down, as in Step 3.</p>"
    )),
    ("// Find an element by its id", [11], (
        "<p>The browser's <code>getElementById</code> returns an element or <code>null</code>. TypeScript makes us deal with the <code>null</code> before we use the result, so this helper stops with a clear message when the page lacks the element. After the check the compiler knows a real element comes back.</p>"
    )),
    ("// Find the elements that we need", [11], (
        "<ul>"
        "<li>The three constants look up elements by <code>id</code> and keep them in variables, so we search the page once and not on every click.</li>"
        "<li><code>as HTMLTemplateElement</code> tells the compiler a fact about our own page that the compiler cannot see.</li>"
        "<li><code>Intl.NumberFormat</code> is a formatter the browser provides. With the locale <code>en-IE</code> and the currency <code>EUR</code> the formatter writes 1.75 as <code>€1.75</code>.</li>"
        "<li>Writing <code>\"€\" + (cents / 100).toFixed(2)</code> works until you meet a place with different conventions, so we let the formatter decide.</li>"
        "</ul>"
    )),
    ("// Send a request to our API", [2, 10], (
        "<p>This function wraps every API call, so the rest of the script never repeats the checks.</p>"
        "<ul>"
        "<li>Inside an <code>async</code> function, <code>await</code> pauses that function, and only that one, until a <dfn>promise</dfn>, an object standing for a value that has not arrived yet, settles. The browser stays responsive meanwhile.</li>"
        "<li><code>fetch</code> sends the request at Station 2, and its reply arrives at Station 10.</li>"
        "<li>If no response arrives at all, <code>fetch</code> rejects, and we turn that into a friendlier message.</li>"
        "<li>If a response arrives with a bad status such as 404 or 409, <code>fetch</code> still counts it as success, so we check <code>response.ok</code> ourselves and pass on the server's own message.</li>"
        "<li><code>&lt;T&gt;</code> lets each caller say what it expects, as in <code>requestJson&lt;Slot[]&gt;(...)</code>. The parsed JSON is typed <code>unknown</code>, the accurate type for data from outside, and the final <code>as T</code> is our claim that the server keeps its side of the contract.</li>"
        "</ul>"
    )),
    ("// Build one card for one slot", [11], (
        "<p>This function turns one slot (the fourth shape from Step 5) into one card (the fifth). <code>cloneNode(true)</code> makes a deep copy of the template, so the template stays unchanged for the next card.</p>"
        "<ul>"
        "<li>The exclamation marks say <em>this is never null</em>, because we wrote the template ourselves. Each one overrides the compiler's caution, so use them only where you know the page.</li>"
        "<li>Every line that shows data uses <code>textContent</code>, which treats the value as plain text. With <code>innerHTML</code>, an item name containing a script tag would run. That attack is cross-site scripting.</li>"
        "<li>The function returns a card that is not on the screen yet, because nothing has attached it to the page.</li>"
        "</ul>"
    )),
    ("// Ask the server for every slot", [10, 11, 12], (
        "<ul>"
        "<li><code>slots.map(createSlotCard)</code> converts an array of data into an array of cards.</li>"
        "<li><code>replaceChildren(...)</code> swaps the contents of <code>#slots</code> for them in one step. That is the moment the DOM changes, and the browser repaints at Station 12.</li>"
        "<li><code>try</code> and <code>catch</code> show any error in the status line. Inside <code>catch</code> the error has type <code>unknown</code>, so <code>as Error</code> states what it is.</li>"
        "</ul>"
    )),
    ("// One listener on the whole list", [1, 2, 10, 11], (
        "<p>We attach one listener to the container and not one to each button, because the buttons do not exist yet when this line runs. A click on a button <dfn>bubbles</dfn> up through its parents, so the container hears it. This is <dfn>event delegation</dfn>, and <code>closest</code> climbs from the clicked element to the nearest Buy button, or returns <code>null</code> when the click landed elsewhere.</p>"
        "<ul>"
        "<li>This function is Station 1.</li>"
        "<li>The function reads the slot id from <code>slotCard.dataset.slot</code>, which is the <code>data-slot</code> attribute that the card carries, sends a <code>POST</code>, and swaps in a new card built from the server's reply.</li>"
        "<li>We draw what the server said and not what we guess, so if someone bought the last item a moment earlier, the card tells the truth.</li>"
        "</ul>"
    )),
    ("// Show the slots as soon", [2], (
        "<p>The last line runs once when the script loads and sends the first request.</p>"
    )),
]

# ------------------------------------------------------------- sections


def fw_html():
    return (
        '<div class="prose"><h3>Where frameworks fit</h3>'
        "<ul>"
        "<li>Real projects rarely write server plumbing by hand. A <dfn>framework</dfn> provides routing, validation, safe static files, error handling and many conveniences.</li>"
        "<li>We wrote the plumbing ourselves so that each mechanism is visible once.</li>"
        "<li>The usual names in the Node world are Express (the oldest and most widely taught), Fastify (validation from a schema, built for speed) and Hono (small, runs on many platforms).</li>"
        "<li>In each of them our route table shrinks to three lines such as <em>on GET /api/slots, call this function</em>, and the framework reads the request, sets the headers and sends the JSON.</li>"
        "<li>All of them sit on the same <code>node:http</code> module that we used, so what you learned here is what they do underneath.</li>"
        "</ul></div>"
    )


E["frameworks_html"] = fw_html()


def sec_build_db():
    body = goal(
        [
            "Create the vending machine's database as a file.",
            "Run a script that fills the database with four slots.",
            "See the stored rows printed back.",
        ]
    )
    body += (
        '<div class="prose"><h3>Two ideas about TypeScript</h3>'
        "<ul>"
        "<li>A <dfn>type</dfn> says what kind of value a variable holds, such as a number or a text. A tool called the <dfn>type checker</dfn> reads these labels and reports mistakes before the program runs.</li>"
        "<li>The labels exist only for the checker. Before the program runs they are erased, and ordinary JavaScript remains.</li>"
        "<li>Node 22.18 and newer can run a TypeScript file directly by erasing the labels as it loads the file. That is <dfn>type stripping</dfn>, and it is why <code>node src/server.ts</code> needs no build step.</li>"
        "<li>A browser cannot do this, so the page script goes through the compiler <code>tsc</code>, which writes a JavaScript file. The server uses stripping, and the page script uses the compiler.</li>"
        "</ul></div>"
    )
    body += concept_database(E)
    body += make_steps(
        [
            "Create a folder called <code>vending-ts</code> and open a terminal in it.",
            "Create <code>package.json</code> with the code below, then run <code>npm install</code>.",
            "Create a folder <code>src</code>, and in it a file <code>setup-db.ts</code> with the second code block.",
            "Run <code>npm run setup-db</code>.",
        ]
    )
    body += file_block(PROJECT, "package.json", PACKAGE_CHUNKS, "json", "in vending-ts/")
    body += file_block(PROJECT, "src/setup-db.ts", SETUP_CHUNKS, "typescript", "in vending-ts/src/")
    body += check(
        [
            "The terminal prints the four rows below, after an experimental warning from Node. The warning is expected.",
            "A new file called <code>vending.db</code> sits in the project folder. That file is the whole database.",
            "Run the script a second time and you get the same four rows. Which line made that safe?",
        ]
    )
    body += snippet(
        "[ 'A1', 'Sparkling Water', 175, 8 ]\n[ 'A2', 'Salted Peanuts', 125, 5 ]\n[ 'B1', 'Chocolate Bar', 200, 3 ]\n[ 'B2', 'Oat Biscuits', 150, 0 ]",
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
        "<li>The diagram below names the functions that you will write in each layer.</li>"
        "</ul></div>"
    )
    body += layers_figure(E["layer_names"], E["slug"])
    body += make_steps(
        [
            "In <code>src</code>, create <code>server.ts</code> and type or paste the first code block below.",
            "In <code>src</code>, create <code>tsconfig.json</code> with the second code block.",
            "Run <code>npm run check</code>. The command prints nothing when the type checker finds no problem.",
            "Run <code>npm start</code>. The server stays running, and that is correct.",
            "Visit <code>http://127.0.0.1:8000/api/slots</code> in a browser.",
        ]
    )
    body += file_block(PROJECT, "src/server.ts", SERVER_CHUNKS, "typescript", "in vending-ts/src/")
    body += file_block(PROJECT, "src/tsconfig.json", SRC_TSCONFIG_CHUNKS, "json", "in vending-ts/src/")
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
        "<li>The page itself has no logic, and it is identical in both editions. The HTML says what exists and the CSS says how it looks.</li>"
        "</ul></div>"
    )
    body += make_steps(
        [
            "In <code>vending-ts</code>, create a folder called <code>public</code>.",
            "In that folder, create <code>index.html</code> and <code>style.css</code> with the code below.",
            "With the server still running, open <code>http://127.0.0.1:8000</code>.",
        ]
    )
    body += file_block(PROJECT, "public/index.html", INDEX_CHUNKS, "html", "in vending-ts/public/")
    body += file_block(PROJECT, "public/style.css", CSS_CHUNKS, "css", "in vending-ts/public/")
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
            "Compile the script to JavaScript for the browser.",
            "Make the Buy button work, so the whole journey from Step 1 happens.",
        ]
    )
    body += (
        '<div class="prose"><p>The script has one job: ask the server for data and change the page to match the reply. '
        "Everything with rules in it, such as the stock count and the validation, lives in the server. The script is TypeScript too, so the compiler checks it against the browser's own descriptions of the page.</p></div>"
    )
    body += concept_shapes(E)
    body += make_steps(
        [
            "Create a folder <code>client</code>, and in it <code>app.ts</code> with the first code block below.",
            "In <code>client</code>, create <code>tsconfig.json</code> with the second code block.",
            "Run <code>npm run build</code>. The compiler writes <code>public/app.js</code>.",
            "Reload <code>http://127.0.0.1:8000</code>.",
        ]
    )
    body += file_block(PROJECT, "client/app.ts", APP_CHUNKS, "typescript", "in vending-ts/client/")
    body += file_block(PROJECT, "client/tsconfig.json", CLIENT_TSCONFIG_CHUNKS, "json", "in vending-ts/client/")
    body += check(
        [
            "Four cards appear: Sparkling Water, Salted Peanuts, Chocolate Bar and Oat Biscuits.",
            "Oat Biscuits is greyed out, because its stock is zero.",
            "Press Buy on Chocolate Bar three times. The count falls to 0 and the button is disabled.",
            "Reload the page. The count stays at 0, because it lives in the database.",
        ]
    )
    body += deeper(
        "What the compiler did to the file",
        "<p>Open <code>public/app.js</code> and compare it with the TypeScript. This is the start of the request function, before and after:</p>"
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
        + "<p>Every label has gone and the logic is untouched. The file in <code>public</code> is generated, so never edit it by hand: change the TypeScript, run <code>npm run build</code>, and reload.</p>",
    )
    body += predict(
        "<p>Suppose the reply took five seconds. What would the visitor see in that time, and how could we improve it? Think about it, then watch the Network tab in Step 6.</p>"
    )
    return section("build-script", "Step 5", "Build the script", body)


# ------------------------------------------------------- the browser demo

SHIM_CHUNKS = [
    ("", [], (
        "<p>Node has a built-in SQLite module, <code>node:sqlite</code>, and a browser has none. <dfn>sql.js</dfn> is the SQLite engine compiled to WebAssembly, a compact format browsers run, and it gives us a real SQLite database inside the page. "
        "Its methods have different names from Node's, so this file wraps sql.js in the small interface that <code>server.ts</code> expects.</p>"
        "<p>The map keeps each database in memory under a file name. Opening the same name twice returns the same database, which is how the setup script and the server share one machine, as they share <code>vending.db</code> on disk.</p>"
    )),
    ("class StatementSync", [6], (
        "<p>A statement object holds one piece of SQL. The <em>constructor</em>, the function that runs when a statement object is created, prepares the SQL at once, so a mistake in the SQL fails when the server starts and not on the first click, as with the real module.</p>"
    )),
    ("  // Return every matching row", [6], (
        "<p><code>all</code> runs the statement with the values the caller passes and collects the rows into an array of objects. The values travel separately from the SQL, so placeholders protect this demo from injection as they do the real server. "
        "The <code>finally</code> block (code that runs whether or not an error happened) frees the statement even if something goes wrong, because sql.js keeps statements in memory until we release them. <code>get</code> is <code>all</code> with only the first row kept.</p>"
    )),
    ("  // Run a statement that changes data", [7], (
        "<p><code>run</code> executes a statement that changes data. SQLite counts the rows changed, and we return that count as <code>changes</code>, the name that <code>buySlot</code> in <code>server.ts</code> reads to find out whether the purchase worked.</p>"
    )),
    ("class DatabaseSync", [6], (
        "<p>The database class has only the three methods our code calls. <code>exec</code> runs SQL, <code>prepare</code> makes a statement, and <code>close</code> does nothing, because a closed in-memory database could never be reopened.</p>"
    )),
]

ADAPTER_CHUNKS = [
    ("", [], (
        "<p>This file is typed like the rest of the project. The <code>Machine</code> type lists the four things the adapter takes from <code>server.ts</code>: the route table and the three error classes.</p>"
        "<p>The real HTTP layer uses <code>node:http</code>, which needs a network, so we write a replacement for that layer only.</p>"
    )),
    ("function createAnswerer", [4], (
        "<p>The function receives the machine and returns an <code>answer</code> function, which takes a method and a path and returns a status and a body. That is the whole job of an HTTP layer, once the network part is removed.</p>"
    )),
    ("      // The same route table", [4, 8], (
        "<p>The loop is the one from the real <code>answerRequest</code>. The loop walks the real <code>ROUTES</code> table, and the first matching row calls the real handler. The data layer then runs real SQL on a real SQLite database, which here lives in the page's memory.</p>"
    )),
    ("      // The same translation", [9], (
        "<p>These lines repeat the translation from errors to status codes, because that translation belonged to the layer we replaced. A request for <code>B2</code>, which has no stock, ends here as a 409 with the same message the real server sends.</p>"
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
        + '<figure class="demo"><iframe src="demo-ts/vending.html" title="The vending machine page, answered by TypeScript running in the browser" height="560" loading="lazy"></iframe>'
        '<figcaption>The vending machine. The page is the real one from the project, and a simulated server answers its requests. '
        'If nothing appears, open <a href="demo-ts/vending.html">the machine on its own page</a>.</figcaption></figure>'
        + tryit(
            "<p>Open the developer tools, choose the <strong>Network</strong> tab, reload the machine's own page, and press Buy. "
            "The <code>/api/slots</code> rows show that a service worker answered, and the response headers include <code>X-Served-By</code>.</p>"
        )
        + deeper(
            "What is real here, and what is simulated",
            "<p>A web page cannot open a network port, so no real server program is running. Five real things are running.</p>"
            "<ul>"
            "<li>The data layer and the route table are copied out of the real <code>server.ts</code> when this page is built, with the types removed.</li>"
            "<li>The real <code>setup-db.ts</code> creates the table.</li>"
            "<li><dfn>sql.js</dfn> supplies a real SQLite database in the page's memory.</li>"
            "<li>The page's own script, compiled from <code>client/app.ts</code>, is the file you will write in Step 5.</li>"
            "<li>A <dfn>service worker</dfn>, a script that sits between a page and the network, catches each request whose address starts with <code>/api/</code> and hands it to the code above.</li>"
            "</ul>"
            "<p>The simulated part is the wire. No bytes travel between two programs, so Stations 3 and 9 of the journey in Step 1 are imitated. Two small files stand in for what a browser lacks: a wrapper, a small layer of code around another tool, that gives sql.js the interface of Node's SQLite module, and a replacement for the HTTP layer. The second is possible because the layers were kept apart.</p>"
            + "<p>The Station badges beside the code point to the journey that Step 1 introduces.</p>"
            + file_block(W / "demo-src", "ts/node-sqlite-shim.js", SHIM_CHUNKS, "javascript", "the stand-in for node:sqlite")
            + file_block(W / "demo-src", "ts/adapter.ts", ADAPTER_CHUNKS, "typescript", "the replacement for the HTTP layer")
            + "<p>The real server's headers include <code>Date</code> and <code>Connection</code>. This reply has neither, because no real server wrote it.</p>",
        )
        + '<div class="prose"><ul>'
        '<li>Want to change the pages, the SQL or the server and watch each request travel? The <a href="workbench/index.html">workbench</a> shows the browser, the server and the database side by side, with a timeline.</li>'
        "<li>When you are ready, start with Step 1. In Step 6 you run a real server on your own computer.</li>"
        "</ul></div>"
    )
    return section("try-first", "Try it first", "The finished machine, running in your browser", body)
