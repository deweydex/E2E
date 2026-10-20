"""Shared teaching text, part two: running the project, then the optional "going deeper" sections and the glossary."""

import re

from lib import annotated, box, check, deeper, esc, goal, make_steps, predict, section, snippet
from shared_a import fill

from diagrams import cors_figure, race_figure


# ------------------------------------------------------------- step 6: run it


def sec_run(E):
    body = goal(
        [
            "Start the project and open it in your browser.",
            "Watch each request arrive, both in the browser and in the terminal.",
            "Call the API without the page, to see that the page is only one client.",
        ]
    )
    body += make_steps(
        [
            "Open a terminal in the project folder and run the commands below.",
            "Open <code>http://127.0.0.1:8000</code> in a browser.",
        ]
    )
    body += snippet(E["run_block"], "bash", "Start the project") + E.get("run_note", "")
    body += check(
        [
            "The page shows four slots. This is stations 1 to 12 happening once, because the script asks for the slots as soon as it loads.",
            "Pressing Buy lowers the stock of that slot by one.",
            "Reloading the page keeps the new number, because it now lives in the database.",
        ]
    )
    body += """
<div class="prose">
<h3>Watch the traffic in the browser</h3>
<ol class="make">
<li>Press F12 to open the developer tools (Ctrl+Shift+I on Windows and Linux, Option+Command+I on a Mac).</li>
<li>Choose the <strong>Network</strong> tab and reload the page. Each row is one message the browser sent: the page, <code>style.css</code>, <code>app.js</code> and <code>slots</code>, which is the API request.</li>
<li>Click the <code>slots</code> row. <strong>Headers</strong> shows the request and the response, and <strong>Response</strong> shows the JSON.</li>
<li>Press Buy. A new row appears, this time a <code>POST</code>. The Status column shows the status code, and the Time column shows the length of the round trip.</li>
</ol>
<h3>Watch the traffic in the terminal</h3>
<p>The server prints one line for each request it answers. Put the terminal beside the browser and press Buy a few times.</p>
</div>
"""
    body += snippet(E["log_sample"], "text", "What the terminal shows", copy=False)
    body += """
<div class="prose">
<p>The browser may also ask for <code>/favicon.ico</code>, the tab's little icon, without being told to. The server has no route for it and answers 404, which is harmless and shows that browsers send requests you never wrote.</p>
<h3>Call the API without the page</h3>
<p>The address bar is a client too. Visit <code>http://127.0.0.1:8000/api/slots</code> and you see the raw JSON. A command line tool called <code>curl</code> is a third client:</p>
</div>
"""
    body += snippet(
        "curl http://127.0.0.1:8000/api/slots\ncurl -i http://127.0.0.1:8000/api/slots/B2\ncurl -i -X POST http://127.0.0.1:8000/api/slots/A1/buy",
        "bash",
        "Three requests from a terminal",
    )
    body += """
<div class="prose">
<ul>
<li><code>-i</code> shows the response headers.</li>
<li><code>-X POST</code> chooses the method.</li>
<li>In older versions of Windows PowerShell, <code>curl</code> is an alias for another command, so type <code>curl.exe</code> instead.</li>
</ul>
</div>
"""
    body += box(
        "note",
        "Why it works",
        "<p>The server does not care who sent a request. The browser, the address bar and <code>curl</code> all send the same kind of message and get the same kind of reply. A phone app would need no change on the server either. That independence is the point of having an API.</p>",
    )
    return section("run", "Step 6", "Run it and watch the traffic", body)


# ----------------------------------------------------------- going deeper: HTTP


def sec_http(E):
    request_items = [
        (
            "POST /api/slots/a1/buy HTTP/1.1",
            "<p>The <dfn>request line</dfn> holds three things: the <dfn>method</dfn> (<code>POST</code>, the kind of action), the <dfn>path</dfn> (which thing it is done to) and the protocol version.</p>",
            [2],
        ),
        (
            "Host: 127.0.0.1:8000\nUser-Agent: curl/8.5.0\nAccept: */*",
            "<p><dfn>Headers</dfn> come next, one per line, each as a name, a colon and a value.</p><ul><li><code>Host</code> names the server the client believes it is talking to.</li><li><code>User-Agent</code> names the client program.</li><li><code>Accept</code> lists the formats the client can read.</li></ul>",
            [2, 3],
        ),
        (
            "",
            "<p>A blank line ends the headers. A <code>POST</code> may carry a <dfn>body</dfn> after it, such as a form or a JSON document. This one has none, because the path already says everything the server needs.</p>",
            [2],
        ),
    ]
    response_items = [
        (E["http_status_line"], E["http_status_note"], [9]),
        (
            E["http_headers"],
            "<p>The response headers describe the body.</p><ul><li><code>Content-Type</code> says how to read it: JSON in UTF-8, the standard way of turning characters into bytes.</li><li><code>Content-Length</code> says how many bytes of body follow.</li><li><code>Cache-Control: no-store</code> asks the browser never to reuse an old copy, so an edit shows up on the next reload.</li></ul>"
            + (f"<p>{E['http_headers_extra']}</p>" if E.get("http_headers_extra") else ""),
            [9],
        ),
        (
            '\n{"slot_id": "A1", "item_name": "Sparkling Water", "price_cents": 175, "stock": 7}'.replace(": ", E["json_colon"]).replace(", ", E["json_comma"]),
            "<p>After the blank line comes the body. This is the JSON that the script parses at Station 10.</p>",
            [8, 9],
        ),
    ]
    status_rows = [
        ("200", "OK", "The request worked and the body holds the result."),
        ("400", "Bad Request", "The client sent something the server cannot make sense of, such as the slot id <code>hello</code>."),
        ("404", "Not Found", "The request was well formed, but nothing exists at that address, such as slot <code>Z9</code>."),
        ("409", "Conflict", "The request was fine but clashes with the current state. Buying from a sold-out slot is a conflict."),
        ("500", "Internal Server Error", "Something broke inside the server. The fault is ours, not the client's."),
    ]
    rows = "".join(f"<tr><td><strong>{c}</strong></td><td>{n}</td><td>{d}</td></tr>" for c, n, d in status_rows)
    body = """
<div class="prose">
<p>You can build the whole project without reading this section. It is here for when you want to know exactly what the browser and the server say to each other.</p>
<ul>
<li>A <dfn>protocol</dfn> is an agreement about the order and shape of messages.</li>
<li><dfn>HTTP</dfn> (HyperText Transfer Protocol) is the agreement that browsers and web servers use.</li>
<li>Every exchange is two plain-text messages, a request and a response. Below is a real pair from the running project.</li>
</ul>
</div>
"""
    body += annotated(request_items, "http", "The request the client sends")
    body += annotated(response_items, "http", "The response the server sends back")
    body += (
        """
<div class="prose">
<h3>Status codes</h3>
<p>The status code is a three digit number that tells the client how things went before it reads the body. The first digit gives the family: 2 means success, 4 means the client made a mistake, and 5 means the server did.</p>
</div>
<div class="tablewrap">
<table class="tbl"><thead><tr><th>Code</th><th>Name</th><th>When we send it</th></tr></thead><tbody>
"""
        + rows
        + """
</tbody></table>
</div>
<div class="prose">
<h3>Methods</h3>
<ul>
<li><code>GET</code> reads something and promises to change nothing. A method like that is <dfn>safe</dfn>.</li>
<li><code>POST</code> asks the server to do something, and it may change data.</li>
<li>Browsers, link previews in chat apps and search engine crawlers send <code>GET</code> requests freely and may repeat them. If buying were a <code>GET</code>, a chat app that previews a link could buy a snack.</li>
<li>Buying is also not <dfn>idempotent</dfn>, because doing it twice does not leave the same result as doing it once. Reading is idempotent, so you can refresh a page as often as you like.</li>
</ul>
<h3>A server with no memory</h3>
<p>HTTP is <dfn>stateless</dfn>: the server treats every request as new and remembers nothing between them. So the stock count lives in the database and never in a variable inside the server.</p>
<h3>REST in one paragraph</h3>
<p>Many web APIs follow a style called <dfn>REST</dfn> (Representational State Transfer). URLs name things with nouns, the method chooses the action, and each request is complete in itself. Our API borrows that style without following every rule of it.</p>
</div>
"""
    )
    return section("http", "Going deeper", "HTTP messages and status codes", body)


# ------------------------------------------------------ going deeper: experiments


def _exp(title, do, see):
    return f'<h3>{title}</h3><div class="prose">{do}</div>{box("try", "What happened, and why", see)}'


def sec_experiments(E):
    sql_tools = (
        "Open <code>vending.db</code> in the free program DB Browser for SQLite, or use the <code>sqlite3</code> command line tool if it is installed. "
        + E["sql_extra"]
    )
    body = (
        goal(
            [
                "Break the machine in seven controlled ways and see which layer notices.",
                "Predict each result before you read the explanation.",
            ],
            "In this section you will",
        )
        + f'<div class="prose"><ul><li>{sql_tools}</li><li>To reset the machine after an experiment, run the setup script again.</li></ul></div>'
    )
    body += _exp(
        "Experiment 1: three kinds of sold out",
        "<ol><li>In the page, press Buy on the Chocolate Bar until it is sold out. The button greys out after the third press.</li>"
        "<li>Send the same purchase from a terminal, where no disabled button can stop you: <code>curl -i -X POST http://127.0.0.1:8000/api/slots/B1/buy</code></li>"
        "<li>Try to break the rule inside the database: <code>UPDATE inventory SET stock = -1 WHERE slot_id = 'A1';</code></li></ol>",
        "<ul><li>The terminal request returns <code>409 Conflict</code>. The server refused, even though the page was bypassed.</li>"
        "<li>The SQL fails with <code>CHECK constraint failed: stock &gt;= 0</code>. The database refused, even though the server was bypassed.</li>"
        "<li>Three layers, three jobs: the button is a courtesy, the server holds the rule and explains it, and the database is the last line of defence.</li></ul>",
    )
    body += _exp(
        "Experiment 2: two kinds of wrong address",
        "<p>Visit <code>http://127.0.0.1:8000/api/slots/hello</code> and then <code>http://127.0.0.1:8000/api/slots/Z9</code>. Guess each status code first.</p>",
        "<ul><li>The first returns 400. <code>hello</code> is not shaped like a slot id, so the client asked badly.</li>"
        "<li>The second returns 404. <code>Z9</code> has the right shape but no such slot exists.</li>"
        "<li>Two codes let a client tell a typing mistake from a missing item.</li></ul>",
    )
    body += _exp(
        "Experiment 3: joining strings versus passing parameters",
        f"<p>Run <code>{E['injection_cmd']}</code>. It looks up a slot twice, once with a normal id and once with the text <code>x' OR '1'='1</code>, using two ways of building the query.</p>"
        + snippet(E["injection_output"], "text", "Output", copy=False),
        "<ul><li>With joined strings, the typed text becomes part of the SQL. The condition <code>OR '1'='1'</code> is true for every row, so all four rows come back. This attack is <dfn>SQL injection</dfn>.</li>"
        "<li>With a parameter, the database receives the SQL and the value separately. The value can only be data, so it matches nothing.</li>"
        "<li>Some drivers also run several statements in one call, and then the same flaw can delete a table.</li>"
        "<li>That is why every query in this project uses a <code>?</code> placeholder.</li></ul>",
    )
    body += _exp(
        "Experiment 4: opening the page straight from disk",
        "<p>With the server still running, double-click <code>public/index.html</code> so that the browser opens it from disk. The page stays on <em>Loading...</em>. Read the errors in the developer console.</p>",
        "<ul><li>The console cannot load <code>file:///app.js</code>. The HTML says <code>/app.js</code>, and a leading slash means <em>from the root of whatever served this page</em>.</li>"
        "<li>Served by our server, the root is the server. Opened from a file, the root is the top of your disk.</li>"
        "<li>A page and its API need a server that delivers both.</li>"
        "<li>On a project site such as GitHub Pages the root is a path like <code>/project-name/</code>, so a leading slash would point to the wrong place there, and a relative link such as <code>app.js</code> would work.</li></ul>",
    )
    body += _exp(
        "Experiment 5: the page on one port and the API on another",
        "<ol>"
        f"<li>Leave the API on port 8000. In a second terminal, serve only the <code>public</code> folder on port 9000, for example {E['static_server']}.</li>"
        f"<li>In the page's script, change the two URLs that begin with <code>/api/</code> so that they begin with <code>http://127.0.0.1:8000/api/</code>. {E['rebuild_note']}</li>"
        "<li>Open <code>http://127.0.0.1:9000</code>.</li></ol>"
        "<p>The page says <em>Cannot reach the server. Is it running?</em>, yet the server is running. Check the console and the server's terminal before you read on.</p>",
        "<ul><li>The console reports a <strong>CORS policy</strong> block. The server's terminal shows that it received the request and answered normally.</li>"
        "<li>The browser delivered the request and then refused to let the script read the answer.</li>"
        "<li>The reason is the <dfn>same-origin policy</dfn>. An <dfn>origin</dfn> is scheme, host and port together, and port 9000 is a different origin from port 8000.</li>"
        "<li>By default a script may read responses only from its own origin. That stops a malicious page from reading your private data out of another site you are signed in to.</li>"
        "<li>A server can opt in with a header. The policy it opts in to is <dfn>CORS</dfn> (Cross-Origin Resource Sharing).</li></ul>"
        f"<p>To fix it, add one header to every response: {E['cors_snippet']} Restart the server and reload, and the page works.</p>"
        "<ul><li>Requests that carry a JSON body or custom headers trigger an extra preliminary <code>OPTIONS</code> request, which the server would also have to answer.</li>"
        "<li>We named the exact origin and not <code>*</code>, which means <em>any website</em>. The wildcard suits public data and is risky when the response depends on who is asking.</li></ul>",
    )
    body += cors_figure()
    body += _exp(
        "Experiment 6: stopping the server",
        "<p>Press Ctrl+C to stop the server, return to the page and press Buy. Look at the status line and the console.</p>",
        "<ul><li>The page shows <em>Cannot reach the server. Is it running?</em>, the same message as Experiment 5, though the cause is different.</li>"
        "<li><code>fetch</code> fails whenever no usable response arrives: the server is down, the network is off or the browser blocked the answer.</li>"
        "<li>A 404 or a 409 still counts as an answer, and <code>fetch</code> does not treat it as a failure.</li>"
        "<li>Think about how the script could give a more accurate message, and whether it can know enough to do so.</li></ul>",
    )
    body += _exp(
        "Experiment 7: changing data without touching any code",
        "<p>With the server running, change a price with <code>UPDATE inventory SET price_cents = 99 WHERE slot_id = 'A1';</code> and reload the page.</p>",
        "<ul><li>Sparkling Water now costs <em>€0.99</em>. Neither the server nor the page was edited or restarted.</li>"
        "<li>The database is the single source of truth, and every request reads it again. That is why data lives in a database and logic lives in code.</li></ul>",
    )
    return section("experiments", "Going deeper", "Break it on purpose", body)


# ---------------------------------------------------------- going deeper: choices


def sec_choices(E):
    rows = [
        ("SQLite for storage",
         "Nothing to install, one file to copy, and the same SQL that bigger systems use.",
         "When many programs or computers write at once, or you need accounts, backups and monitoring at scale, a server database such as PostgreSQL fits better."),
        (E["choice_server_title"], E["choice_server_why"], E["choice_server_when"]),
        (E["choice_conn_title"], E["choice_conn_why"], E["choice_conn_when"]),
        ("The same server delivers the page and the API",
         "Both share one origin, so no CORS settings are needed, and only one program has to start.",
         "When the page lives on a static host such as GitHub Pages and the API lives elsewhere, the origins differ. The API then needs CORS headers and HTTPS."),
        ("JSON replies, with the page building its own elements",
         "The page and the API stay independent, and the same API can serve a phone app.",
         "When a page must work without scripts, the server can send finished HTML, and a form with a full page reload replaces the script."),
        ("Prices stored as whole cents",
         "Whole numbers are exact, so sums never drift.",
         "Some databases have an exact decimal type, which is also fine. A floating point column for money is never a good choice."),
        ("POST for buying",
         "Buying changes data and is not idempotent, so a link preview must not be able to trigger it.",
         "Other changes use other methods: PUT to replace something, PATCH to adjust part of it, DELETE to remove it."),
        ("Parameterised queries everywhere",
         "The database receives SQL and values separately, so a value can never turn into SQL.",
         "There is no good reason to choose differently."),
        ("One UPDATE with <code>AND stock &gt; 0</code>",
         "A single statement checks and changes together. Reading first and writing afterwards leaves a gap in which two buyers could both take the last item.",
         "When a purchase needs several steps, group them in one explicit transaction, and think about what the database does when two transactions collide."),
        ("Rules in three places",
         "The page is a convenience, the server holds the rules and explains them, and the database is the last line of defence.",
         "You may drop the check in the page, because a visitor can skip it anyway. The server and database checks stay."),
        ("<code>textContent</code> rather than <code>innerHTML</code>",
         "<code>textContent</code> treats a value as plain text. <code>innerHTML</code> parses it as markup, so an item name containing a script tag could run code in every visitor's browser. That attack is cross-site scripting (<dfn>XSS</dfn>).",
         "<code>innerHTML</code> is fine for markup you wrote yourself and never for data from elsewhere."),
        ("A <code>&lt;template&gt;</code> element for the card",
         "The structure of a card stays in HTML, where it is easy to read and restyle, and not inside strings in the script.",
         "Front end frameworks such as React and Svelte generate this part for you and become worthwhile as pages grow."),
        ("Redrawing the card from the server's reply",
         "The page shows what the server says, so it cannot drift from the truth. If somebody bought the last item a second ago, the reply says so.",
         "An <em>optimistic</em> update shows the change first and corrects it if the server disagrees. It feels faster on a slow network and costs more code."),
        ("A fixed list of files that the server will send",
         "A server that sent whatever file the URL named could be asked for its own source code or the database file. That attack is <dfn>path traversal</dfn>.",
         "A framework's static file helper handles this safely, so use it instead of writing your own."),
    ]
    trs = "".join(f"<tr><td><strong>{a}</strong></td><td>{b}</td><td>{c}</td></tr>" for a, b, c in rows)
    body = fill(
        f"""
<div class="prose">
<p>Almost every line in this project was a choice, and most had a respectable alternative. For each choice the table gives the reason we chose as we did and the situation where you would choose differently. When you build your own project, ask yourself those same two questions about each decision.</p>
</div>
<div class="tablewrap">
<table class="tbl"><thead><tr><th>The choice</th><th>Why it fits here</th><th>When you might choose differently</th></tr></thead><tbody>{trs}</tbody></table>
</div>
<div class="prose"><h3>Why one UPDATE beats read-then-write</h3>
<p>The diagram shows the race that a single <code>UPDATE</code> prevents. The same pattern of a check followed by a change appears in booking systems, bank transfers and ticket sales.</p></div>
{race_figure()}
{E["frameworks_html"]}
""",
        E,
    )
    return section("choices", "Going deeper", "Design choices and alternatives", body)


# --------------------------------------------------------- going deeper: extensions


def sec_extensions(E):
    items = [
        ("A restock route.",
         f"Add <code>POST /api/slots/A1/restock</code> with a JSON body such as <code>{{\"amount\": 5}}</code>. Reject a missing body, invalid JSON and an amount that is not a whole number from 1 to 100, each with a 400. {E['body_hint']}"),
        ("A sales log in the same transaction.",
         "Create a <code>sales</code> table with an id, a slot id that references <code>inventory</code>, a timestamp and the price paid. Make a purchase insert a sale and decrement the stock inside one transaction. Why should the sale store the price again? Then prove the transaction works: raise an error between the two statements and check that the stock did not change."),
        ("A summary route.",
         "Add <code>GET /api/sales/summary</code> that returns, for each item, how many were sold and how much money they earned. This needs a <code>JOIN</code> and a <code>GROUP BY</code>, and the result has to arrive as clean JSON."),
        ("Automatic refresh.",
         "Make the page ask for the slots every five seconds with <code>setInterval</code>, and open it in two windows. When you buy in one, how long until the other notices? Server-sent events and WebSockets let the server push changes instead."),
        ("Separate hosting.",
         "Serve the page from its own port and make it work with CORS, as in Experiment 5. Then think about hosting only the page on GitHub Pages. You would need an absolute API address, a CORS header for your Pages origin, and an API reachable over HTTPS, because a page served over HTTPS may not call an insecure address."),
    ]
    if E.get("extra_extension"):
        items.append(E["extra_extension"])
    lis = "".join(f"<li><strong>{t}</strong> {d}</li>" for t, d in items)
    body = f"""
<div class="prose">
<p>Each extension below is small and practises one idea from this tutorial. They are problems to approach your own way, and the hints say where to start and no more.</p>
<ol>{lis}</ol>
</div>
"""
    return section("extensions", "Going deeper", "Extend it yourself", body)


# ------------------------------------------------------------------- glossary

# Each term is explained in the step or section named in REFERENCES.
GLOSSARY = [
    ("API", "Application Programming Interface. The part of a program that other programs may use, and the ways they may ask it to do things."),
    ("Body", "The data that follows the headers in a request or a response, such as the JSON of a slot."),
    ("Client", "A program that starts a conversation with a server. Our browser is the client."),
    ("Connection", "An open line of communication between a program and a database."),
    ("Constraint", "A rule that the database enforces on its own, such as NOT NULL or CHECK (stock >= 0)."),
    ("Contract", "The agreed shape of requests and replies in an API: which fields exist and what type each has."),
    ("CORS", "Cross-Origin Resource Sharing. Headers with which a server allows a page from another origin to read its responses."),
    ("Database management system", "A program that stores data safely and answers queries about it, for example SQLite or PostgreSQL."),
    ("DOM", "Document Object Model. The browser's live tree of objects, one for every element on the page."),
    ("Endpoint", "One address of an API, such as /api/slots/A1."),
    ("Event", "A message that the browser creates when something happens on the page, such as a click."),
    ("Event delegation", "Listening for events on a parent element instead of on each child, which also covers children added later."),
    ("fetch", "The browser function that sends an HTTP request from a script and returns a promise."),
    ("Handler", "The function that answers one kind of request."),
    ("Header", "A name and value that describe a request or a response, such as Content-Type."),
    ("Host", "The name or number that says which computer a request goes to."),
    ("HTTP", "HyperText Transfer Protocol. The agreed text format of requests and responses between browsers and servers."),
    ("Idempotent", "Describes an action that leaves the same result whether you do it once or many times."),
    ("JSON", "JavaScript Object Notation. A text format for structured data, used by most web APIs."),
    ("Method", "The word in a request that says what kind of action is wanted, such as GET or POST."),
    ("Origin", "The combination of scheme, host and port. Pages may read responses only from their own origin unless the server allows more."),
    ("Parameterised query", "A query in which values travel separately from the SQL text, marked by placeholders such as ?."),
    ("Parsing", "Turning text into a structure that a program can use, such as JSON text into an object."),
    ("Path", "The part of a URL after the port, such as /api/slots."),
    ("Path traversal", "An attack that uses parts such as /../ in a URL to reach files that were never meant to be served."),
    ("Port", "A number that tells the operating system which waiting program should receive a message."),
    ("Primary key", "A column whose value is different in every row, so it identifies exactly one row."),
    ("Promise", "An object that stands for a value that has not arrived yet."),
    ("Protocol", "An agreement about the order and shape of messages."),
    ("Relational database", "A database that keeps its data in tables of rows and columns."),
    ("Request", "A message from a client that says what it wants."),
    ("Response", "The message a server sends back, made of a status code, headers and a body."),
    ("REST", "Representational State Transfer. A style of web API in which URLs name things and methods choose the action."),
    ("Route", "A pairing of a method and a path pattern with the function that handles it."),
    ("Safe method", "A method that changes nothing on the server, such as GET."),
    ("Same-origin policy", "The browser rule that stops a page from reading responses that come from another origin."),
    ("Schema", "The declared structure of a database: its tables, columns and types."),
    ("Serialising", "Turning a structure in memory into text or bytes so that it can be stored or sent."),
    ("Server", "A program that waits for requests and answers them."),
    ("SQL", "Structured Query Language. The language for asking a relational database to find or change rows."),
    ("SQL injection", "An attack in which text typed by a user becomes part of an SQL statement."),
    ("Stateless", "Describes a server that treats every request as new and remembers nothing between them."),
    ("Status code", "The three digit number at the start of a response that says how the request went."),
    ("Transaction", "A group of database steps that either all happen or none happen."),
    ("URL", "Uniform Resource Locator. The address of something on the web, made of scheme, host, port and path."),
    ("Validation", "Testing that input is well formed before using it."),
    ("XSS", "Cross-site scripting. An attack that gets a page to run a script that arrived as data."),
]

REFERENCES = {
    "Step 1": ["Connection", "DOM", "Event", "Handler", "JSON", "Promise", "Request", "Response", "Route", "SQL", "Transaction", "Validation"],
    "Step 2": ["Constraint", "Database management system", "Primary key", "Relational database", "Schema"],
    "Step 3": ["API", "Client", "Contract", "Endpoint", "Host", "Path", "Port", "Server", "URL"],
    "Step 5": ["Event delegation", "fetch", "Parsing", "Serialising"],
    "HTTP messages": ["Body", "Header", "HTTP", "Idempotent", "Method", "Protocol", "REST", "Safe method", "Stateless", "Status code"],
    "Break it on purpose": ["CORS", "Origin", "Parameterised query", "Same-origin policy", "SQL injection"],
    "Design choices": ["Path traversal", "XSS"],
}


def sec_glossary(E):
    where = {term: place for place, terms in REFERENCES.items() for term in terms}
    missing = [t for t, _ in GLOSSARY if t not in where]
    assert not missing, "glossary terms without a reference: " + ", ".join(missing)
    items = "".join(
        f"<div><dt>{esc(t)}</dt><dd>{esc(d)} <span class=\"where\">({where[t]})</span></dd></div>"
        for t, d in sorted(GLOSSARY, key=lambda x: x[0].lower())
    )
    body = f"""
<div class="prose">
<p>Terms in alphabetical order. The name in brackets shows where the term is explained.</p>
</div>
<dl class="glossary">{items}</dl>
"""
    return section("glossary", "Reference", "Glossary", body)
