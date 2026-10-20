"""Shared concept sections, part two: running, experiments, choices, extensions, glossary."""

from lib import box, esc, predict, section, snippet, tryit
from shared_a import fill

from diagrams import cors_figure, race_figure


def sec_run(E):
    body = fill(
        """
<div class="prose">
<p>Now we run the whole thing and look at the traffic. You start the project with these commands in a terminal, inside the project folder:</p>
</div>
""",
        E,
    ) + snippet(E["run_block"], "bash", "Starting the project") + E.get("run_note", "") + fill(
        """
<div class="prose">
<p>Then you open <code>http://127.0.0.1:8000</code> in a browser. The page shows the four slots, and that means stations 1 to 12 have already happened once, because the script asks for the list of slots as soon as it loads.</p>
<h3>Watching the traffic in the browser</h3>
<p>Open the developer tools with F12 (or Ctrl+Shift+I, or Option+Command+I on a Mac), choose the <strong>Network</strong> tab, and reload the page. You see one row for each message the browser sent: the page itself, <code>style.css</code>, <code>app.js</code>, and <code>slots</code>, which is the API request. Click the <code>slots</code> row. The Headers view shows the request and the response in the layout we studied in Part 4, and the Response view shows the JSON. Now press Buy on a slot and watch a new row appear, this time a <code>POST</code>. The Status column shows the status code, and the Time column shows how long the whole round trip took.</p>
<h3>Watching the traffic in the terminal</h3>
<p>The server prints one line for each request it answers. Place the terminal beside the browser and press Buy a few times. Each press leaves one line:</p>
</div>
""",
        E,
    ) + snippet(E["log_sample"], "text", "What the terminal shows", copy=False) + fill(
        """
<div class="prose">
<p>Your browser may also ask for <code>/favicon.ico</code>, the little icon for the tab, without being told to. Our server has no route for it and answers 404, which is a harmless demonstration that the browser sends requests that we never wrote.</p>
<h3>Using the API without the page</h3>
<p>The page is only one client of the API. Another client is the address bar. If you visit <code>http://127.0.0.1:8000/api/slots</code> you see the raw JSON, with no page at all. A third client is a command line tool called <code>curl</code>:</p>
</div>
""",
        E,
    ) + snippet(
        "curl http://127.0.0.1:8000/api/slots\ncurl -i http://127.0.0.1:8000/api/slots/B2\ncurl -i -X POST http://127.0.0.1:8000/api/slots/A1/buy",
        "bash",
        "Three requests from a terminal",
    ) + fill(
        """
<div class="prose">
<p>The <code>-i</code> option shows the response headers, and <code>-X POST</code> chooses the method. In older versions of Windows PowerShell, <code>curl</code> is an alias for a different command, so you may need to type <code>curl.exe</code>. A phone app would be a fourth client, and none of these clients would need any change on the server. That independence is the point of having an API.</p>
</div>
""",
        E,
    )
    return section("run", "Part 11", "Running it and watching the traffic", body)


def _exp(title, do, see):
    return f'<h3>{title}</h3><div class="prose">{do}</div>{box("try", "What happened, and why", see)}'


def sec_experiments(E):
    sql_tools = (
        "You can open <code>vending.db</code> in the free program DB Browser for SQLite, or use the <code>sqlite3</code> command line tool if it is installed. "
        + E["sql_extra"]
    )
    body = fill(
        f"""
<div class="prose">
<p>A system teaches you most when it fails in front of you. Each experiment below breaks something in a controlled way. Try to predict the outcome before you run it, and then compare your prediction with the explanation that follows. After each experiment you can reset the machine by running the setup script again.</p>
<p>{sql_tools}</p>
</div>
""",
        E,
    )
    body += _exp(
        "Experiment 1: three kinds of sold out",
        "<p>In the page, press Buy on the Chocolate Bar until it is sold out. The button greys out after the third press. Now send the same purchase from a terminal, where no disabled button can stop you: <code>curl -i -X POST http://127.0.0.1:8000/api/slots/B1/buy</code>. Finally, try to break the rule inside the database itself, by running <code>UPDATE inventory SET stock = -1 WHERE slot_id = 'A1';</code> in your SQLite tool.</p>",
        "<p>The terminal request returns <code>409 Conflict</code> with a message, so the server refused even though the page had been bypassed. The SQL statement fails with <code>CHECK constraint failed: stock &gt;= 0</code>, so the database refused even though the server had been bypassed. We now have three layers with three jobs. The disabled button is a courtesy to the visitor, the server holds the rule and explains it kindly, and the database is the last line of defence.</p>",
    )
    body += _exp(
        "Experiment 2: two kinds of wrong address",
        "<p>Visit <code>http://127.0.0.1:8000/api/slots/hello</code> and then <code>http://127.0.0.1:8000/api/slots/Z9</code>. Notice which status code each one returns before you read the next paragraph.</p>",
        "<p>The first returns 400 and the second returns 404. The word <code>hello</code> is not shaped like a slot id, so the client made a mistake in how it asked. The id <code>Z9</code> has the right shape, but no such slot exists, so the question was fine and the answer is <em>nothing here</em>. Splitting those two cases lets a client tell a typing mistake from a missing item.</p>",
    )
    body += _exp(
        "Experiment 3: joining strings versus passing parameters",
        f"<p>Run <code>{E['injection_cmd']}</code>. The script looks up a slot twice, once with a normal id and once with the text <code>x' OR '1'='1</code>, and it does so with two different methods of building the query. The output looks like this:</p>"
        + snippet(E["injection_output"], "text", "Output", copy=False),
        "<p>When the query is built by joining strings, the text typed by the user becomes part of the SQL itself, and the condition <code>OR '1'='1'</code> is true for every row, so all four rows come back. This attack is called <dfn>SQL injection</dfn>. When the value travels as a parameter, the database receives the SQL and the value separately, and so the value can only ever be data. It matches no slot id and returns nothing. Some drivers also allow several statements in one call, and in those the same flaw lets an attacker delete a table. That is why every query in this project uses a <code>?</code> placeholder, even when the value comes from our own validated code.</p>",
    )
    body += _exp(
        "Experiment 4: opening the page straight from disk",
        "<p>Double-click <code>public/index.html</code> in your file manager so that the browser opens it from disk, with the server still running. The page stays on <em>Loading...</em>. Open the developer console and read the errors.</p>",
        "<p>The console reports that it cannot load <code>file:///app.js</code>. In the HTML we wrote <code>/app.js</code>, and a path that starts with a slash means <em>from the root of whatever served this page</em>. Our server is that root when it serves the page, but from a file the root is the top of your disk. Two lessons follow. A page and its API need a server that delivers both, and links that start with a slash behave differently depending on where the page is hosted. A project site on GitHub Pages lives under a path such as <code>/project-name/</code>, so a link that starts with a slash would point at the wrong place there, and relative links such as <code>app.js</code> would work.</p>",
    )
    body += _exp(
        "Experiment 5: the page on one port and the API on another",
        f"<p>Leave the API running on port 8000. In a second terminal, serve only the <code>public</code> folder on port 9000 with any static file server, for example {E['static_server']}. In the page's script, change the two URLs that begin with <code>/api/</code> so that they begin with <code>http://127.0.0.1:8000/api/</code>. {E['rebuild_note']}Then open <code>http://127.0.0.1:9000</code>.</p>"
        "<p>The page says <em>Cannot reach the server. Is it running?</em>, yet the server is running. Check the console and check the server's terminal before you read on.</p>",
        "<p>The console says the request was blocked by <strong>CORS policy</strong>, and the terminal shows that the server received the request and answered it normally. The browser delivered the request, then refused to let the script read the answer. The reason is the <dfn>same-origin policy</dfn>. An <dfn>origin</dfn> is the combination of scheme, host and port, and <code>127.0.0.1:9000</code> is a different origin from <code>127.0.0.1:8000</code>. By default a script may read responses only from its own origin, which stops a malicious page from reading your private data out of another site you are signed in to. A server can opt in with a header, and the policy it opts in to is called <dfn>CORS</dfn> (Cross-Origin Resource Sharing).</p>"
        f"<p>To fix it, add one header to every response: {E['cors_snippet']} Restart the server and reload. The page now works, and the Buy button works too. Requests that carry a JSON body or custom headers trigger an extra preliminary check, an <code>OPTIONS</code> request, which a server would then have to answer as well. We chose the exact origin for the header and not <code>*</code>, which means <em>any website</em>. That wildcard is acceptable for public data, and it is risky when the response depends on who is asking.</p>",
    )
    body += cors_figure()
    body += _exp(
        "Experiment 6: stopping the server",
        "<p>Stop the server with Ctrl+C, return to the page that is served from it, and press Buy. Look at the status line and at the console.</p>",
        "<p>The page shows <em>Cannot reach the server. Is it running?</em> and the console reports a refused connection. That is the same message that Experiment 5 produced, even though the cause was different. <code>fetch</code> rejects its promise whenever no usable response arrives, whether the server is down, the network is off or the browser blocked the answer. A response that arrives with a 404 or a 409 counts as an answer, and <code>fetch</code> does not treat it as a failure. You might think about how the script could give the visitor a more accurate message, and whether it can know enough to do so.</p>",
    )
    body += _exp(
        "Experiment 7: changing data without touching any code",
        "<p>With the server running, change a price with <code>UPDATE inventory SET price_cents = 99 WHERE slot_id = 'A1';</code> in your SQLite tool, and then reload the page.</p>",
        "<p>The price of Sparkling Water becomes <em>€0.99</em>. Neither the server nor the page was edited or restarted. The database is the single source of truth, and every request reads it again. That is why we keep data in a database and logic in code.</p>",
    )
    return section("experiments", "Part 12", "Breaking it on purpose", body)


def sec_choices(E):
    rows = [
        ("SQLite for storage",
         "Nothing to install, one file to copy, and the same SQL that bigger systems use.",
         "When many programs or many computers write at once, or when you need accounts, backups and monitoring at scale, a server database such as PostgreSQL fits better."),
        (E["choice_server_title"], E["choice_server_why"], E["choice_server_when"]),
        (E["choice_conn_title"], E["choice_conn_why"], E["choice_conn_when"]),
        ("The same server delivers the page and the API",
         "Both share one origin, so no CORS settings are needed, and there is only one program to start.",
         "When the page lives on a static host such as GitHub Pages and the API lives elsewhere, the origins differ, and the API must send CORS headers and be reachable over HTTPS."),
        ("JSON replies, with the page building its own elements",
         "The page and the API stay independent, and the same API can serve a phone app or another program.",
         "When a page must work without scripts, the server can send finished HTML instead. A form and a full page reload then replace the script."),
        ("Prices stored as whole cents",
         "Whole numbers are exact, so sums never drift.",
         "Some databases offer an exact decimal type, and you can use that. A floating point column for money is never a good choice."),
        ("POST for buying",
         "Buying changes data and is not idempotent, so it must not be something that a link preview can trigger.",
         "Other changes may use other methods. Many APIs use PUT to replace something, PATCH to adjust part of it and DELETE to remove it."),
        ("Parameterised queries everywhere",
         "The database receives SQL and values separately, so a value can never turn into SQL.",
         "There is no good reason to choose differently."),
        ("One UPDATE with <code>AND stock &gt; 0</code>",
         "A single statement checks and changes together. Reading first and writing afterwards leaves a gap in which two simultaneous buyers could both take the last item.",
         "When a purchase needs several steps, group them in one explicit transaction, and think about what the database does when two transactions collide."),
        ("Rules in three places",
         "The page offers convenience, the server holds the rules and explains them, and the database is the last line of defence.",
         "You may drop the check in the page, because a visitor can skip it anyway. The checks in the server and the database stay."),
        ("<code>textContent</code> rather than <code>innerHTML</code>",
         "<code>textContent</code> treats a value as plain text. <code>innerHTML</code> parses it as markup, so an item name that contained a script tag could run code in every visitor's browser. That attack is called cross-site scripting (XSS).",
         "<code>innerHTML</code> is acceptable for markup that you wrote yourself and never for data that came from somewhere else."),
        ("A <code>&lt;template&gt;</code> element for the card",
         "The structure of a card stays in HTML, where it is easy to read and to restyle, instead of hiding inside strings in the script.",
         "Front end frameworks such as React and Svelte generate this part for you, and they become worthwhile as pages grow."),
        ("Redrawing the card from the server's reply",
         "The page shows what the server says, so it cannot drift away from the truth. If somebody else bought the last item a second ago, the reply says so.",
         "An <em>optimistic</em> update shows the change first and corrects it if the server disagrees. It feels faster on a slow network and costs more code."),
        ("A fixed list of files that the server will send",
         "A server that sent whatever file the URL named could be asked for the server's own source code or for the database file itself. That attack is called path traversal.",
         "A framework's static file helper handles this safely, and you should use it instead of writing your own."),
    ]
    trs = "".join(f"<tr><td><strong>{a}</strong></td><td>{b}</td><td>{c}</td></tr>" for a, b, c in rows)
    body = fill(
        f"""
<div class="prose">
<p>Almost every line in this project was a choice, and most choices had a respectable alternative. The table lists the main ones, with the reason we chose as we did and the situation in which you would choose differently. When you build your own project, a useful habit is to ask the same two questions about each decision.</p>
</div>
<div class="tablewrap">
<table class="tbl"><thead><tr><th>The choice</th><th>Why it fits here</th><th>When you might choose differently</th></tr></thead><tbody>{trs}</tbody></table>
</div>
<div class="prose"><h3>Why one UPDATE beats read-then-write</h3><p>The diagram below shows the race that the single <code>UPDATE</code> prevents. It is worth studying, because the same pattern of a check followed by a change appears in booking systems, bank transfers and ticket sales.</p></div>
{race_figure()}
{E["frameworks_html"]}
""",
        E,
    )
    return section("choices", "Part 13", "The choices we made, and the alternatives", body)


def sec_extensions(E):
    items = [
        ("A restock route.",
         f"Add <code>POST /api/slots/A1/restock</code> with a JSON body such as <code>{{\"amount\": 5}}</code>. The route must reject a missing body, a body that is not valid JSON, and an amount that is not a whole number from 1 to 100, and each rejection should be a 400. {E['body_hint']}"),
        ("A sales log in the same transaction.",
         "Create a <code>sales</code> table with an id, a slot id that references <code>inventory</code>, a timestamp and the price paid. Make a purchase insert a sale row and decrement the stock inside one transaction. Why should the sale store the price again instead of looking it up later? Then prove that the transaction works: raise an error between the two statements and check that the stock did not change."),
        ("A summary route.",
         "Add <code>GET /api/sales/summary</code> that returns, for each item, how many were sold and how much money they earned. This needs a <code>JOIN</code> and a <code>GROUP BY</code>, so it is a good place to practise SQL where the result has to arrive as clean JSON."),
        ("Automatic refresh.",
         "Make the page ask for the list of slots every five seconds with <code>setInterval</code>, and open the page in two windows. When you buy in one window, how long until the other window notices? Polling like this is the most direct approach, and techniques such as server-sent events and WebSockets let the server push changes to the page instead."),
        ("Separate hosting.",
         "Serve the page from its own port and make it work properly with CORS, as in Experiment 5. Then think about what you would change to host only the page on GitHub Pages while the API runs somewhere else. You would need an absolute API address, a CORS header for the origin of your Pages site, and an API reachable over HTTPS, because a page served over HTTPS may not call an insecure address."),
    ]
    if E.get("extra_extension"):
        items.append(E["extra_extension"])
    lis = "".join(f"<li><strong>{t}</strong> {d}</li>" for t, d in items)
    body = f"""
<div class="prose">
<p>When the project works, you can grow it. Each of these extensions is small and exercises a different idea from this page. They are written as problems for you to approach in your own way, and the hints say where to start and no more.</p>
<ol>{lis}</ol>
</div>
"""
    return section("extensions", "Part 14", "Extending it yourself", body)


GLOSSARY = [
    ("API", "Application Programming Interface. The agreed ways one program may ask another to do things. (Part 5)"),
    ("Body", "The data that follows the headers in a request or a response, such as the JSON of a slot. (Part 4)"),
    ("Client", "A program that starts a conversation with a server. Our browser is the client. (Part 4)"),
    ("Connection", "An open line of communication between a program and a database. (Part 1)"),
    ("Constraint", "A rule that the database enforces on its own, such as NOT NULL or CHECK (stock >= 0). (Part 2)"),
    ("Contract", "The agreed shape of requests and replies in an API: which fields exist and what type each has. (Part 5)"),
    ("CORS", "Cross-Origin Resource Sharing. Headers with which a server allows a page from another origin to read its responses. (Part 12)"),
    ("Database management system", "A program that stores data safely and answers queries about it, for example SQLite or PostgreSQL. (Part 2)"),
    ("DOM", "Document Object Model. The browser's live tree of objects, one for every element on the page. (Part 1)"),
    ("Endpoint", "One address of an API, such as /api/slots/A1. (Part 5)"),
    ("Event", "A message that the browser creates when something happens on the page, such as a click. (Part 1)"),
    ("Event delegation", "Listening for events on a parent element instead of on each child, which also covers children added later. (Part 10)"),
    ("fetch", "The browser function that sends an HTTP request from a script and returns a promise. (Part 10)"),
    ("Handler", "The function that answers one kind of request. (Part 1)"),
    ("Header", "A name and value that describe a request or a response, such as Content-Type. (Part 4)"),
    ("Host", "The name or number that says which computer a request goes to. (Part 4)"),
    ("HTTP", "HyperText Transfer Protocol. The agreed text format of requests and responses between browsers and servers. (Part 4)"),
    ("Idempotent", "Describes an action that leaves the same result whether you do it once or many times. (Part 5)"),
    ("JSON", "JavaScript Object Notation. A text format for structured data, used by most web APIs. (Part 1)"),
    ("Method", "The word in a request that says what kind of action is wanted, such as GET or POST. (Part 4)"),
    ("Origin", "The combination of scheme, host and port. Pages may read responses only from their own origin unless the server allows more. (Part 12)"),
    ("Parameterised query", "A query in which values travel separately from the SQL text, marked by placeholders such as ?. (Part 12)"),
    ("Parsing", "Turning text into a structure that a program can use, such as JSON text into an object. (Part 6)"),
    ("Path", "The part of a URL after the port, such as /api/slots. (Part 4)"),
    ("Path traversal", "An attack that uses parts such as /../ in a URL to reach files that were never meant to be served. (Part 13)"),
    ("Port", "A number that tells the operating system which waiting program should receive a message. (Part 4)"),
    ("Primary key", "A column whose value is different in every row, so it identifies exactly one row. (Part 2)"),
    ("Promise", "An object that stands for a value that has not arrived yet. (Part 1)"),
    ("Protocol", "An agreement about the order and shape of messages. (Part 4)"),
    ("Relational database", "A database that keeps its data in tables of rows and columns. (Part 2)"),
    ("Request", "A message from a client that says what it wants. (Part 1)"),
    ("Response", "The message a server sends back, made of a status code, headers and a body. (Part 1)"),
    ("REST", "Representational State Transfer. A style of web API in which URLs name things and methods choose the action. (Part 5)"),
    ("Route", "A pairing of a method and a path pattern with the function that handles it. (Part 1)"),
    ("Safe method", "A method that changes nothing on the server, such as GET. (Part 5)"),
    ("Same-origin policy", "The browser rule that stops a page from reading responses that come from another origin. (Part 12)"),
    ("Schema", "The declared structure of a database: its tables, columns and types. (Part 2)"),
    ("Serialising", "Turning a structure in memory into text or bytes so that it can be stored or sent. (Part 6)"),
    ("Server", "A program that waits for requests and answers them. (Part 1)"),
    ("SQL", "Structured Query Language. The language for asking a relational database to find or change rows. (Part 1)"),
    ("SQL injection", "An attack in which text typed by a user becomes part of an SQL statement. (Part 12)"),
    ("Stateless", "Describes a server that treats every request as new and remembers nothing between them. (Part 4)"),
    ("Status code", "The three digit number at the start of a response that says how the request went. (Part 4)"),
    ("Transaction", "A group of database steps that either all happen or none happen. (Part 1)"),
    ("URL", "Uniform Resource Locator. The address of something on the web, made of scheme, host, port and path. (Part 4)"),
    ("Validation", "Testing that input is well formed before using it. (Part 1)"),
    ("XSS", "Cross-site scripting. An attack that gets a page to run a script that arrived as data. (Part 13)"),
]


def sec_glossary(E):
    items = "".join(f"<div><dt>{esc(t)}</dt><dd>{esc(d)}</dd></div>" for t, d in sorted(GLOSSARY, key=lambda x: x[0].lower()))
    body = f"""
<div class="prose">
<p>The terms below appear in this tutorial, in alphabetical order. Each entry names the part where the term is first explained in detail.</p>
</div>
<dl class="glossary">{items}</dl>
"""
    return section("glossary", "Reference", "Glossary", body)
